import React from "react";
import { useCurrentFrame, interpolate, Easing } from "remotion";

interface StickmanProps {
    action: string; // idle, wave, point, walk, happy, sad
    color?: string;
    accentColor?: string;
    lineWidth?: number;
    scale?: number;
}

export const Stickman: React.FC<StickmanProps> = ({
    action = "idle",
    color = "#000000",
    accentColor = "#3498db",
    lineWidth = 3,
    scale = 1.0,
}) => {
    const frame = useCurrentFrame();

    // Animation: tay vẫy nhẹ theo frame
    const waveAngle = interpolate(
        frame % 30,
        [0, 15, 30],
        [0, 15, 0],
        { extrapolateRight: "clamp" }
    );

    // Animation: walk cycle
    const walkOffset = interpolate(
        frame % 40,
        [0, 10, 20, 30, 40],
        [0, 5, 0, -5, 0],
        { extrapolateRight: "clamp" }
    );

    // Breathing animation nhẹ
    const breathe = interpolate(
        frame % 60,
        [0, 30, 60],
        [1, 1.01, 1],
        { extrapolateRight: "clamp" }
    );

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
    } else if (action === "point") {
        rightArmPath = `M${shoulderRX},${shoulderRY} L195,95`;
    } else {
        rightArmPath = `M${shoulderRX},${shoulderRY} L150,165`;
    }

    // Chân: walk hoặc idle
    let legLPath = "", legRPath = "";
    if (action === "walk") {
        const offset = walkOffset;
        legLPath = `M${80},${bodyBottom} L${55 + offset},225 L${35 + offset},275`;
        legRPath = `M${120},${bodyBottom} L${145 - offset},225 L${165 - offset},275`;
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
        bottom: "5%",
        right: "10%",
        width: `${200 * scale}px`,
        height: `${300 * scale}px`,
        transform: `scale(${breathe})`,
        transformOrigin: "bottom center",
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
            <path d={`M${headX},${neckY} L${shoulderLX},${shoulderLY} L${handLX},${handLY}`}
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
