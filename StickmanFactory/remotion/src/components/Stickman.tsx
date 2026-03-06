import React from "react";
import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";

interface StickmanProps {
    action: string; // idle, wave, point, walk, happy, sad, explain, counting, writing, sitting, fist_pump
    actionFrame?: number; // relative frame to sync animation bouncing on pose change
    positionX?: number; // base position 0 is right 10%
    color?: string;
    accentColor?: string;
    lineWidth?: number;
    scale?: number;
}

export const Stickman: React.FC<StickmanProps> = ({
    action = "idle",
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

    // Animation: tay vẫy nhẹ theo frame
    const waveAngle = interpolate(
        frame % 30,
        [0, 15, 30],
        [0, 15, 0],
        { extrapolateRight: "clamp" }
    );

    // Animation: walk cycle and translation
    const walkOffset = interpolate(
        frame % 30, // Faster walk cycle 0.5s
        [0, 7.5, 15, 22.5, 30],
        [0, 8, 0, -8, 0],
        { extrapolateRight: "clamp" }
    );

    const walkTranslate = action === "walk" ? interpolate(
        activeFrame, // Use activeFrame so walk starts from current position on action change
        [0, 300], // move 30% of screen over 10s
        [0, -30],
        { extrapolateRight: "clamp" }
    ) : 0;

    // Breathing animation nhẹ - Scale Y lên xuống nhịp nhàng
    // Math.sin cho phép tính toán deterministically cho từng frame độc lập
    const breatheAmount = Math.sin(frame / 10) * 0.02; // Nhún Y 2%
    const scaleY = 1 + breatheAmount;

    // Hiệu ứng nảy (spring bounce) khi đổi dáng (actionFrame 0)
    const bounce = spring({
        frame: activeFrame,
        fps,
        config: { damping: 10, mass: 0.5, stiffness: 100 },
    });

    // Kết hợp scale truyền vào + spring bounce
    const currentScale = scale * interpolate(bounce, [0, 1], [0.8, 1]);

    // Joints cố định
    const headX = 100, headY = 45, headR = 25;
    const neckY = 70;
    const bodyBottom = 180;
    const shoulderLX = 60, shoulderLY = 95;
    const shoulderRX = 140, shoulderRY = 95;

    // Tay trái luôn buông
    const handLX = 50, handLY = 165;

    // Tay phải: thay đổi theo action
    let rightArmPath = "";
    if (action === "wave") {
        const angle = waveAngle;
        const elbowX = 155, elbowY = 60;
        const handRX = 175 + angle * 0.5, handRY = 25 - angle * 0.3;
        rightArmPath = `M${shoulderRX},${shoulderRY} L${elbowX},${elbowY} L${handRX},${handRY}`;
    } else if (action === "point" || action === "counting") {
        rightArmPath = `M${shoulderRX},${shoulderRY} L195,95`;
    } else if (action === "explain") {
        rightArmPath = `M${shoulderRX},${shoulderRY} L185,65`;
    } else if (action === "writing" || action === "counting") {
        // Hand moves slightly around the chest area
        const moveX = 160 + Math.sin(activeFrame / 2) * 10;
        const moveY = 130 + Math.cos(activeFrame / 3) * 5;
        rightArmPath = `M${shoulderRX},${shoulderRY} L${moveX},${moveY}`;
    } else if (action === "fist_pump") {
        rightArmPath = `M${shoulderRX},${shoulderRY} L160,20`;
    } else {
        rightArmPath = `M${shoulderRX},${shoulderRY} L150,165`;
    }

    // Tay trái (Explain mode tay trái cũng mở)
    let leftArmPath = `M${headX},${neckY} L${shoulderLX},${shoulderLY} L${handLX},${handLY}`;
    if (action === "explain") {
        leftArmPath = `M${headX},${neckY} L${shoulderLX},${shoulderLY} L15,65`;
    } else if (action === "fist_pump") {
        leftArmPath = `M${headX},${neckY} L${shoulderLX},${shoulderLY} L40,20`;
    }

    // Chân: walk hoặc idle hoặc sitting
    let legLPath = "", legRPath = "";
    if (action === "walk") {
        const offset = walkOffset;
        legLPath = `M${80},${bodyBottom} L${55 + offset},225 L${35 + offset},275`;
        legRPath = `M${120},${bodyBottom} L${145 - offset},225 L${165 - offset},275`;
    } else if (action === "sitting") {
        legLPath = `M${80},${bodyBottom} L40,${bodyBottom} L40,250`;
        legRPath = `M${120},${bodyBottom} L160,${bodyBottom} L160,250`;
    } else {
        legLPath = `M${80},${bodyBottom} L70,230 L65,280`;
        legRPath = `M${120},${bodyBottom} L130,230 L135,280`;
    }

    // Biểu cảm: miệng
    let mouthPath = "";
    if (action === "happy") {
        mouthPath = `M${headX - 8},${headY + 8} Q${headX},${headY + 18} ${headX + 8},${headY + 8}`;
    } else if (action === "sad") {
        mouthPath = `M${headX - 6},${headY + 14} Q${headX},${headY + 6} ${headX + 6},${headY + 14}`;
    } else {
        mouthPath = `M${headX - 6},${headY + 10} L${headX + 6},${headY + 10}`;
    }

    const svgStyle: React.CSSProperties = {
        position: "absolute",
        bottom: action === "sitting" ? "2%" : "5%",
        right: `${10 + positionX + walkTranslate}%`,
        width: `${200 * currentScale}px`,
        height: `${300 * currentScale}px`,
        transform: `scaleY(${scaleY}) translateX(${interpolate(spring({ frame: activeFrame, fps, config: { damping: 15 } }), [0, 1], [50, 0])}px)`,
        transformOrigin: "bottom center",
        opacity: interpolate(activeFrame, [0, 10], [0, 1], { extrapolateRight: "clamp" })
    };

    return (
        <svg
            viewBox="0 0 200 300"
            style={svgStyle}
            xmlns="http://www.w3.org/2000/svg"
        >
            {/* Head */}
            <circle
                cx={headX} cy={headY} r={headR}
                fill="none" stroke={color} strokeWidth={lineWidth}
                strokeLinecap="round"
            />

            {/* Eyes */}
            <circle cx={headX - 8} cy={headY - 3} r={2.5} fill={color} />
            <circle cx={headX + 8} cy={headY - 3} r={2.5} fill={color} />

            {/* Mouth */}
            <path d={mouthPath} fill="none" stroke={color} strokeWidth={2}
                strokeLinecap="round" />

            {/* Body */}
            <line x1={headX} y1={neckY} x2={headX} y2={bodyBottom}
                stroke={color} strokeWidth={lineWidth} strokeLinecap="round" />

            {/* Left arm */}
            <path d={leftArmPath}
                fill="none" stroke={color} strokeWidth={lineWidth} strokeLinecap="round" />

            {/* Right arm */}
            <path d={rightArmPath}
                fill="none" stroke={color} strokeWidth={lineWidth} strokeLinecap="round" />

            {/* Wave hand circle */}
            {action === "wave" && (
                <circle cx={175 + waveAngle * 0.5} cy={25 - waveAngle * 0.3}
                    r={4} fill={color} />
            )}

            {/* Point arrow */}
            {action === "point" && (
                <>
                    <line x1={185} y1={88} x2={195} y2={95}
                        stroke={color} strokeWidth={2} strokeLinecap="round" />
                    <line x1={185} y1={102} x2={195} y2={95}
                        stroke={color} strokeWidth={2} strokeLinecap="round" />
                </>
            )}

            {/* Legs */}
            <path d={legLPath} fill="none" stroke={color} strokeWidth={lineWidth}
                strokeLinecap="round" />
            <path d={legRPath} fill="none" stroke={color} strokeWidth={lineWidth}
                strokeLinecap="round" />

            {/* Sad tear */}
            {action === "sad" && (
                <circle cx={headX - 10} cy={headY + 3} r={2}
                    fill={accentColor} opacity={0.8} />
            )}
        </svg>
    );
};
