import React from "react";
import { useCurrentFrame, interpolate } from "remotion";

interface SubtitleProps {
    text: string;
    durationInFrames: number;
}

export const Subtitle: React.FC<SubtitleProps> = ({
    text,
    durationInFrames,
}) => {
    const frame = useCurrentFrame();

    // Fade in/out
    const opacity = interpolate(
        frame,
        [0, 10, durationInFrames - 10, durationInFrames],
        [0, 1, 1, 0],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );

    // Cắt text nếu quá dài (an toàn cho màn hình)
    const maxLength = 120;
    const displayText = text.length > maxLength
        ? text.substring(0, maxLength) + "..."
        : text;

    const containerStyle: React.CSSProperties = {
        position: "absolute",
        bottom: "12%",
        left: "5%",
        right: "5%",
        display: "flex",
        justifyContent: "center",
        opacity,
    };

    const textBoxStyle: React.CSSProperties = {
        backgroundColor: "rgba(0, 0, 0, 0.65)",
        borderRadius: "12px",
        padding: "16px 32px",
        maxWidth: "85%",
    };

    const textStyle: React.CSSProperties = {
        color: "#FFFFFF",
        fontSize: "32px",
        fontFamily: "'Arial', 'Helvetica Neue', sans-serif",
        fontWeight: 700,
        textAlign: "center",
        lineHeight: 1.4,
        textShadow: "2px 2px 4px rgba(0,0,0,0.8)",
        letterSpacing: "0.02em",
    };

    return (
        <div style={containerStyle}>
            <div style={textBoxStyle}>
                <span style={textStyle}>{displayText}</span>
            </div>
        </div>
    );
};
