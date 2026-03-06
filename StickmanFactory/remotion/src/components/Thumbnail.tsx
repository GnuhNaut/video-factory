import React from "react";
import { AbsoluteFill, staticFile } from "remotion";

interface ThumbnailProps {
    title: string;
    style?: string;
    width?: number;
    height?: number;
}

const STYLES: Record<string, { bg: string[]; textColor: string; accentColor: string }> = {
    high_contrast: {
        bg: ["#1a1a2e", "#16213e", "#0f3460"],
        textColor: "#FFFFFF",
        accentColor: "#e94560",
    },
    vibrant: {
        bg: ["#667eea", "#764ba2", "#f093fb"],
        textColor: "#FFFFFF",
        accentColor: "#ffd700",
    },
    minimal: {
        bg: ["#2d3436", "#636e72", "#b2bec3"],
        textColor: "#FFFFFF",
        accentColor: "#00cec9",
    },
};

export const Thumbnail: React.FC<ThumbnailProps> = ({
    title,
    style = "high_contrast",
    width = 1280,
    height = 720,
}) => {
    const colors = STYLES[style] || STYLES.high_contrast;

    const bgGradient = `linear-gradient(135deg, ${colors.bg.join(", ")})`;

    return (
        <AbsoluteFill
            style={{
                background: bgGradient,
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                padding: "60px",
                fontFamily: "'Inter', 'Roboto', sans-serif",
            }}
        >
            {/* Decorative circles */}
            <div
                style={{
                    position: "absolute",
                    top: -80,
                    right: -80,
                    width: 300,
                    height: 300,
                    borderRadius: "50%",
                    background: colors.accentColor,
                    opacity: 0.15,
                }}
            />
            <div
                style={{
                    position: "absolute",
                    bottom: -60,
                    left: -60,
                    width: 250,
                    height: 250,
                    borderRadius: "50%",
                    background: colors.accentColor,
                    opacity: 0.1,
                }}
            />

            {/* Main title */}
            <div
                style={{
                    color: colors.textColor,
                    fontSize: 72,
                    fontWeight: 900,
                    textAlign: "center",
                    textTransform: "uppercase",
                    lineHeight: 1.1,
                    letterSpacing: "-2px",
                    textShadow: `4px 4px 0px ${colors.accentColor}, 8px 8px 0px rgba(0,0,0,0.3)`,
                    maxWidth: "90%",
                    zIndex: 10,
                }}
            >
                {title}
            </div>

            {/* Accent line */}
            <div
                style={{
                    width: 120,
                    height: 6,
                    background: colors.accentColor,
                    marginTop: 30,
                    borderRadius: 3,
                    zIndex: 10,
                }}
            />

            {/* Stickman character (simplified) */}
            <svg
                width="150"
                height="200"
                viewBox="0 0 150 200"
                style={{
                    position: "absolute",
                    bottom: 40,
                    right: 60,
                    opacity: 0.9,
                    zIndex: 10,
                }}
            >
                {/* Head */}
                <circle cx="75" cy="35" r="25" fill="none" stroke={colors.textColor} strokeWidth="4" />
                {/* Smile */}
                <path d="M 62 40 Q 75 55 88 40" fill="none" stroke={colors.textColor} strokeWidth="3" />
                {/* Body */}
                <line x1="75" y1="60" x2="75" y2="130" stroke={colors.textColor} strokeWidth="4" />
                {/* Arms (celebrating) */}
                <line x1="75" y1="85" x2="30" y2="55" stroke={colors.textColor} strokeWidth="4" />
                <line x1="75" y1="85" x2="120" y2="55" stroke={colors.textColor} strokeWidth="4" />
                {/* Legs */}
                <line x1="75" y1="130" x2="45" y2="185" stroke={colors.textColor} strokeWidth="4" />
                <line x1="75" y1="130" x2="105" y2="185" stroke={colors.textColor} strokeWidth="4" />
            </svg>

            {/* Brand badge */}
            <div
                style={{
                    position: "absolute",
                    bottom: 20,
                    left: 30,
                    color: colors.textColor,
                    opacity: 0.5,
                    fontSize: 16,
                    fontWeight: 600,
                    letterSpacing: "3px",
                    textTransform: "uppercase",
                }}
            >
                Stickman Factory
            </div>
        </AbsoluteFill>
    );
};
