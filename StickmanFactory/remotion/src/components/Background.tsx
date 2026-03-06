import React from "react";
import { useCurrentFrame, interpolate, Img, staticFile } from "remotion";

interface BackgroundProps {
    imagePath: string;
    effect?: string; // zoom_in, zoom_in_slow, zoom_out, zoom_out_slow, pan_left, pan_right, pan_up, none
    durationInFrames: number;
}

export const Background: React.FC<BackgroundProps> = ({
    imagePath,
    effect = "none",
    durationInFrames,
}) => {
    const frame = useCurrentFrame();

    // Ken Burns effects (Continuous smooth zoom/pan across the entire scene)
    let transform = "";
    if (effect === "zoom_in") {
        const scaleIn = interpolate(frame, [0, durationInFrames], [1, 1.15], { extrapolateRight: "clamp" });
        transform = `scale(${scaleIn})`;
    } else if (effect === "zoom_in_slow") {
        const scaleInSlow = interpolate(frame, [0, durationInFrames], [1, 1.05], { extrapolateRight: "clamp" });
        transform = `scale(${scaleInSlow})`;
    } else if (effect === "zoom_out") {
        const scaleOut = interpolate(frame, [0, durationInFrames], [1.15, 1], { extrapolateRight: "clamp" });
        transform = `scale(${scaleOut})`;
    } else if (effect === "zoom_out_slow") {
        const scaleOutSlow = interpolate(frame, [0, durationInFrames], [1.05, 1], { extrapolateRight: "clamp" });
        transform = `scale(${scaleOutSlow})`;
    } else if (effect === "pan_left") {
        const panL = interpolate(frame, [0, durationInFrames], [0, -40], { extrapolateRight: "clamp" });
        transform = `scale(1.1) translateX(${panL}px)`;
    } else if (effect === "pan_right") {
        const panR = interpolate(frame, [0, durationInFrames], [0, 40], { extrapolateRight: "clamp" });
        transform = `scale(1.1) translateX(${panR}px)`;
    } else if (effect === "pan_up") {
        const panU = interpolate(frame, [0, durationInFrames], [0, -30], { extrapolateRight: "clamp" });
        transform = `scale(1.1) translateY(${panU}px)`;
    } else {
        // none
        transform = "scale(1)";
    }

    const containerStyle: React.CSSProperties = {
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        overflow: "hidden",
    };

    const imgStyle: React.CSSProperties = {
        width: "100%",
        height: "100%",
        objectFit: "cover",
        transform,
        transformOrigin: "center center",
    };

    return (
        <div style={containerStyle}>
            <Img src={staticFile(imagePath)} style={imgStyle} />
        </div>
    );
};
