import React from "react";
import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";

interface StickmanProps {
    action: string;
    previousAction?: string; // used for smooth transition
    actionFrame?: number;
    positionX?: number;
    color?: string;
    accentColor?: string;
    lineWidth?: number;
    scale?: number;
}

// Define explicit joint coordinates
interface StickmanPose {
    headX: number; headY: number; neckY: number;
    shoulderLX: number; shoulderLY: number; handLX: number; handLY: number;
    shoulderRX: number; shoulderRY: number; elbowRX?: number; elbowRY?: number; handRX: number; handRY: number;
    bodyBottom: number;
    kneeLX?: number; kneeLY?: number; footLX: number; footLY: number;
    kneeRX?: number; kneeRY?: number; footRX: number; footRY: number;
}

const getPose = (action: string, waveAngle: number, walkOffset: number, actionFrame: number): StickmanPose => {
    // Base joints
    const pose: StickmanPose = {
        headX: 100, headY: 45, neckY: 70,
        shoulderLX: 60, shoulderLY: 95, handLX: 50, handLY: 165,
        shoulderRX: 140, shoulderRY: 95, handRX: 150, handRY: 165,
        bodyBottom: 180,
        footLX: 65, footLY: 280, kneeLX: 70, kneeLY: 230,
        footRX: 135, footRY: 280, kneeRX: 130, kneeRY: 230
    };

    // Right arm
    if (action === "wave") {
        pose.elbowRX = 155; pose.elbowRY = 60;
        pose.handRX = 175 + waveAngle * 0.5; pose.handRY = 25 - waveAngle * 0.3;
    } else if (action === "point" || action === "counting" || action === "pointing") {
        pose.handRX = 195; pose.handRY = 95;
    } else if (action === "explain") {
        pose.handRX = 185; pose.handRY = 65;
    } else if (action === "writing") {
        pose.handRX = 160 + Math.sin(actionFrame / 2) * 10;
        pose.handRY = 130 + Math.cos(actionFrame / 3) * 5;
    } else if (action === "fist_pump") {
        pose.handRX = 160; pose.handRY = 20;
    }

    // Left arm
    if (action === "explain") {
        pose.handLX = 15; pose.handLY = 65;
    } else if (action === "fist_pump") {
        pose.handLX = 40; pose.handLY = 20;
    }

    // Legs
    if (action === "walk" || action === "walking") {
        pose.kneeLX = 70 + walkOffset; pose.kneeLY = 230;
        pose.footLX = 65 + walkOffset; pose.footLY = 280;
        pose.kneeRX = 130 - walkOffset; pose.kneeRY = 230;
        pose.footRX = 135 - walkOffset; pose.footRY = 280;
    } else if (action === "run") {
        pose.kneeLX = 70 + walkOffset * 1.5; pose.kneeLY = 210;
        pose.footLX = 40 + walkOffset * 2; pose.footLY = 270;
        pose.kneeRX = 130 - walkOffset * 1.5; pose.kneeRY = 210;
        pose.footRX = 160 - walkOffset * 2; pose.footRY = 270;
        pose.headY = 50; // Lean forward slightly
    } else if (action === "sitting") {
        pose.kneeLX = 40; pose.kneeLY = pose.bodyBottom;
        pose.footLX = 40; pose.footLY = 250;
        pose.kneeRX = 160; pose.kneeRY = pose.bodyBottom;
        pose.footRX = 160; pose.footRY = 250;
        pose.bodyBottom = 170; // Slightly lower
    }

    return pose;
};

export const Stickman: React.FC<StickmanProps> = ({
    action = "idle",
    previousAction = "idle",
    actionFrame,
    positionX = 0,
    color = "#000000",
    accentColor = "#3498db",
    lineWidth = 3,
    scale = 1.0,
}) => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();
    const activeFrame = actionFrame !== undefined ? actionFrame : frame;

    // Active wave/walk cycles
    // Active wave/walk cycles
    const waveAngle = interpolate(frame % 30, [0, 15, 30], [0, 15, 0], { extrapolateRight: "clamp" });

    // Run is faster than walk
    const cycleDuration = action === "run" ? 15 : 30;
    const walkOffset = interpolate(frame % cycleDuration, [0, cycleDuration / 4, cycleDuration / 2, cycleDuration * 0.75, cycleDuration], [0, 12, 0, -12, 0], { extrapolateRight: "clamp" });

    // Transition progress between previousAction and action
    const transitionProgress = spring({
        frame: activeFrame,
        fps,
        config: { damping: 14, mass: 0.5, stiffness: 120 },
    });

    const prevPose = getPose(previousAction, previousAction === "wave" ? waveAngle : 0, previousAction === "walk" ? walkOffset : 0, activeFrame);
    const targetPose = getPose(action, action === "wave" ? waveAngle : 0, action === "walk" ? walkOffset : 0, activeFrame);

    // Interpolate all joints
    const interp = (key: keyof StickmanPose) => {
        const p1 = prevPose[key] ?? targetPose[key] ?? 0;
        const p2 = targetPose[key] ?? prevPose[key] ?? 0;
        return p1 + (p2 - p1) * transitionProgress;
    };

    const pose: StickmanPose = {
        headX: interp("headX"), headY: interp("headY"), neckY: interp("neckY"),
        shoulderLX: interp("shoulderLX"), shoulderLY: interp("shoulderLY"), handLX: interp("handLX"), handLY: interp("handLY"),
        shoulderRX: interp("shoulderRX"), shoulderRY: interp("shoulderRY"), handRX: interp("handRX"), handRY: interp("handRY"),
        bodyBottom: interp("bodyBottom"),
        footLX: interp("footLX"), footLY: interp("footLY"), footRX: interp("footRX"), footRY: interp("footRY")
    };

    // Optional knees & elbows if present in either
    if (prevPose.elbowRX !== undefined || targetPose.elbowRX !== undefined) {
        pose.elbowRX = interp("elbowRX"); pose.elbowRY = interp("elbowRY");
    }
    if (prevPose.kneeLX !== undefined || targetPose.kneeLX !== undefined) {
        pose.kneeLX = interp("kneeLX"); pose.kneeLY = interp("kneeLY");
        pose.kneeRX = interp("kneeRX"); pose.kneeRY = interp("kneeRY");
    }

    // SVG Paths
    const rightArmPath = pose.elbowRX !== undefined
        ? `M${pose.shoulderRX},${pose.shoulderRY} L${pose.elbowRX},${pose.elbowRY} L${pose.handRX},${pose.handRY}`
        : `M${pose.shoulderRX},${pose.shoulderRY} L${pose.handRX},${pose.handRY}`;

    const leftArmPath = `M${pose.headX},${pose.neckY} L${pose.shoulderLX},${pose.shoulderLY} L${pose.handLX},${pose.handLY}`;

    const legLPath = pose.kneeLX !== undefined
        ? `M80,${pose.bodyBottom} L${pose.kneeLX},${pose.kneeLY} L${pose.footLX},${pose.footLY}`
        : `M80,${pose.bodyBottom} L${pose.footLX},${pose.footLY}`;

    const legRPath = pose.kneeRX !== undefined
        ? `M120,${pose.bodyBottom} L${pose.kneeRX},${pose.kneeRY} L${pose.footRX},${pose.footRY}`
        : `M120,${pose.bodyBottom} L${pose.footRX},${pose.footRY}`;

    // Mouth calculation (does not need complex interp, just snap for simplicity or small blend)
    let mouthPath = `M${pose.headX - 6},${pose.headY + 10} L${pose.headX + 6},${pose.headY + 10}`;
    if (action === "happy") mouthPath = `M${pose.headX - 8},${pose.headY + 8} Q${pose.headX},${pose.headY + 18} ${pose.headX + 8},${pose.headY + 8}`;
    else if (action === "sad" || action === "tired") mouthPath = `M${pose.headX - 6},${pose.headY + 14} Q${pose.headX},${pose.headY + 6} ${pose.headX + 6},${pose.headY + 14}`;

    // Horizontal movement for walk/run
    const isMoving = action === "walk" || action === "walking" || action === "run";
    const moveTranslate = isMoving
        ? interpolate(activeFrame, [0, 90], [50, -50], { extrapolateRight: "clamp" })
        : 0;

    // Breathing effect
    const breatheAmount = Math.sin(frame / 10) * 0.02;
    const scaleY = 1 + breatheAmount;

    // Bounce effect only on the start of a scene (activeFrame close to 0) if no previousAction is given
    const currentScale = scale * (previousAction === "idle" && activeFrame < 15 ? interpolate(transitionProgress, [0, 1], [0.8, 1]) : 1);

    const svgStyle: React.CSSProperties = {
        position: "absolute",
        bottom: action === "sitting" ? "2%" : "5%",
        right: `${10 + positionX + moveTranslate}%`,
        width: `${200 * currentScale}px`,
        height: `${300 * currentScale}px`,
        transform: `scaleY(${scaleY})`,
        transformOrigin: "bottom center",
        opacity: interpolate(activeFrame, [0, 10], [0, 1], { extrapolateRight: "clamp" })
    };

    return (
        <svg viewBox="0 0 200 300" style={svgStyle} xmlns="http://www.w3.org/2000/svg">
            <line x1={pose.headX} y1={pose.neckY} x2={pose.headX} y2={pose.bodyBottom} stroke={color} strokeWidth={lineWidth} strokeLinecap="round" />
            <path d={leftArmPath} fill="none" stroke={color} strokeWidth={lineWidth} strokeLinecap="round" />
            <path d={rightArmPath} fill="none" stroke={color} strokeWidth={lineWidth} strokeLinecap="round" />
            <path d={legLPath} fill="none" stroke={color} strokeWidth={lineWidth} strokeLinecap="round" />
            <path d={legRPath} fill="none" stroke={color} strokeWidth={lineWidth} strokeLinecap="round" />

            <circle cx={pose.headX} cy={pose.headY} r={25} fill="none" stroke={color} strokeWidth={lineWidth} strokeLinecap="round" />
            <circle cx={pose.headX - 8} cy={pose.headY - 3} r={2.5} fill={color} />
            <circle cx={pose.headX + 8} cy={pose.headY - 3} r={2.5} fill={color} />
            <path d={mouthPath} fill="none" stroke={color} strokeWidth={2} strokeLinecap="round" />

            {action === "wave" && <circle cx={pose.handRX} cy={pose.handRY} r={4} fill={color} />}
            {(action === "point" || action === "pointing" || action === "counting") && (
                <>
                    <line x1={pose.handRX - 10} y1={pose.handRY - 7} x2={pose.handRX} y2={pose.handRY} stroke={color} strokeWidth={2} strokeLinecap="round" />
                    <line x1={pose.handRX - 10} y1={pose.handRY + 7} x2={pose.handRX} y2={pose.handRY} stroke={color} strokeWidth={2} strokeLinecap="round" />
                </>
            )}
            {(action === "sad" || action === "tired") && <circle cx={pose.headX - 10} cy={pose.headY + 3} r={2} fill={accentColor} opacity={0.8} />}
        </svg>
    );
};
