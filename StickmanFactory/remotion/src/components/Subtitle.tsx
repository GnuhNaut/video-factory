import React from "react";
import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import { loadFont } from "@remotion/google-fonts/Inter";

// Load font at the top level
const { fontFamily } = loadFont();

interface SubtitleProps {
    text: string;
    durationInFrames: number;
}

export const Subtitle: React.FC<SubtitleProps> = ({
    text,
    durationInFrames,
}) => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();

    // Fade in/out scene total
    const opacity = interpolate(
        frame,
        [0, 5, durationInFrames - 5, durationInFrames],
        [0, 1, 1, 0],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );

    // Cắt text nếu quá dài
    const maxLength = 150;
    const displayText = text.length > maxLength
        ? text.substring(0, maxLength) + "..."
        : text;

    const words = displayText.split(" ");

    // Spread word animations over 80% of the scene duration
    const durationPerWord = (durationInFrames * 0.8) / Math.max(words.length, 1);

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
        fontFamily, // Used loaded Inter font
        fontWeight: 700,
        textAlign: "center",
        lineHeight: 1.4,
        textShadow: "2px 2px 4px rgba(0,0,0,0.8)",
        letterSpacing: "0.02em",
    };

    return (
        <div style={containerStyle}>
            <div style={textBoxStyle}>
                <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '8px' }}>
                    {words.map((word, index) => {
                        // Delay mỗi từ tuần tự
                        const delayForThisWord = index * durationPerWord;

                        // Tính toán spring bounce cho từ này
                        const wordScale = spring({
                            fps,
                            frame: frame - delayForThisWord,
                            config: {
                                damping: 12,
                                stiffness: 200,
                                mass: 0.5,
                            },
                        });

                        // Đổi màu vàng highlight một nhịp (nảy xong về trắng)
                        const colorHighlight = interpolate(
                            frame - delayForThisWord,
                            [0, 5, 20],
                            [0, 1, 0],
                            { extrapolateRight: "clamp", extrapolateLeft: "clamp" }
                        );

                        const r = Math.round(255);
                        const g = Math.round(interpolate(colorHighlight, [0, 1], [255, 215]));
                        const b = Math.round(interpolate(colorHighlight, [0, 1], [255, 0]));

                        return (
                            <span
                                key={index}
                                style={{
                                    ...textStyle,
                                    transform: `scale(${wordScale})`,
                                    display: 'inline-block',
                                    color: `rgb(${r}, ${g}, ${b})`,
                                }}
                            >
                                {word}
                            </span>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};
