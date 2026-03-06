import React from "react";
import { useCurrentFrame, interpolate, Img, staticFile, useVideoConfig } from "remotion";

export interface TimelineItem {
    time_offset: number;
    bg_image_path?: string;
    camera_effect?: string;
}

interface BackgroundProps {
    timeline: TimelineItem[];
    durationInFrames: number;
}

export const Background: React.FC<BackgroundProps> = ({
    timeline,
    durationInFrames,
}) => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();
    const CROSSFADE_FRAMES = 15;

    const containerStyle: React.CSSProperties = {
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        overflow: "hidden",
    };

    return (
        <div style={containerStyle}>
            {timeline.map((item, index) => {
                if (!item.bg_image_path) return null;

                const startFrame = Math.round(item.time_offset * fps);

                // End frame is either the start of the next item, or the end of the scene
                const nextItem = timeline[index + 1];
                const endFrame = nextItem
                    ? Math.round(nextItem.time_offset * fps)
                    : durationInFrames;

                // Opacity: Fade in over CROSSFADE_FRAMES, fade out over CROSSFADE_FRAMES (if there's a next item)
                const opacity = interpolate(
                    frame,
                    [
                        startFrame - CROSSFADE_FRAMES,
                        startFrame,
                        endFrame - (nextItem ? CROSSFADE_FRAMES : 0),
                        endFrame
                    ],
                    [index === 0 ? 1 : 0, 1, 1, nextItem ? 0 : 1],
                    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
                );

                // Ken Burns 
                const effect = item.camera_effect || "none";
                let transform = "";

                // We use relative frame for transform
                const relativeFrame = Math.max(0, frame - startFrame);
                const itemDuration = endFrame - startFrame;

                if (effect === "zoom_in") {
                    transform = `scale(${interpolate(relativeFrame, [0, itemDuration], [1, 1.15], { extrapolateRight: "clamp" })})`;
                } else if (effect === "zoom_in_slow") {
                    transform = `scale(${interpolate(relativeFrame, [0, itemDuration], [1, 1.05], { extrapolateRight: "clamp" })})`;
                } else if (effect === "zoom_out") {
                    transform = `scale(${interpolate(relativeFrame, [0, itemDuration], [1.15, 1], { extrapolateRight: "clamp" })})`;
                } else if (effect === "zoom_out_slow") {
                    transform = `scale(${interpolate(relativeFrame, [0, itemDuration], [1.05, 1], { extrapolateRight: "clamp" })})`;
                } else if (effect === "pan_left") {
                    transform = `scale(1.1) translateX(${interpolate(relativeFrame, [0, itemDuration], [0, -40], { extrapolateRight: "clamp" })}px)`;
                } else if (effect === "pan_right") {
                    transform = `scale(1.1) translateX(${interpolate(relativeFrame, [0, itemDuration], [0, 40], { extrapolateRight: "clamp" })}px)`;
                } else if (effect === "pan_up") {
                    transform = `scale(1.1) translateY(${interpolate(relativeFrame, [0, itemDuration], [0, -30], { extrapolateRight: "clamp" })}px)`;
                } else {
                    transform = "scale(1)";
                }

                return (
                    <Img
                        key={index}
                        src={staticFile(item.bg_image_path)}
                        style={{
                            position: "absolute",
                            width: "100%",
                            height: "100%",
                            objectFit: "cover",
                            transform,
                            transformOrigin: "center center",
                            opacity,
                            zIndex: index
                        }}
                    />
                );
            })}
        </div>
    );
};
