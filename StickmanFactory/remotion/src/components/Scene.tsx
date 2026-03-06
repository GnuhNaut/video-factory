import React from "react";
import { Audio, useVideoConfig, staticFile, useCurrentFrame, interpolate, spring } from "remotion";
import { Stickman } from "./Stickman";
import { Background } from "./Background";
import { Subtitle } from "./Subtitle";

interface SceneData {
    scene_id: number;
    text: string;
    audio_path: string;
    bg_image_path?: string;
    character_state?: string;
    character_action?: string;
    actions?: Array<{
        time_start: number;
        action: string;
        emotion_icon?: string;
        b_roll?: string
    }>;
    camera_effect?: string;
    actual_duration?: number;
    expected_duration?: number;
}

interface SceneProps {
    data: SceneData;
    durationInFrames: number;
    transitionFrames?: number;
}

export const Scene: React.FC<SceneProps> = ({ data, durationInFrames, transitionFrames = 0 }) => {
    const { fps } = useVideoConfig();
    const frame = useCurrentFrame();

    // Determine stickman action based on timeline
    let action = "idle";
    let actionFrame = frame;
    let emotionIcon = "";
    let bRoll = "";

    if (data.actions && data.actions.length > 0) {
        const currentTime = frame / fps;
        let activeActionObj = data.actions[0];

        for (const act of data.actions) {
            if (act.time_start <= currentTime) {
                activeActionObj = act;
            }
        }

        action = mapAction(activeActionObj.action);
        emotionIcon = activeActionObj.emotion_icon || "";
        bRoll = activeActionObj.b_roll || "";

        const actionStartFrame = Math.round(activeActionObj.time_start * fps);
        actionFrame = Math.max(0, frame - actionStartFrame);
    } else {
        // Fallback for older JSONs
        action = data.character_action && data.character_action !== "none"
            ? mapAction(data.character_action)
            : data.character_state ? mapAction(data.character_state) : "idle";
    }

    // Smooth transition fade in/out
    const opacity = interpolate(
        frame,
        [
            0,
            transitionFrames,
            durationInFrames - transitionFrames,
            durationInFrames
        ],
        [transitionFrames > 0 ? 0 : 1, 1, 1, transitionFrames > 0 ? 0 : 1],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );

    const containerStyle: React.CSSProperties = {
        position: "relative",
        width: "100%",
        height: "100%",
        overflow: "hidden",
        backgroundColor: "#1a1a2e",
        opacity,
    };

    // Emotion bounce
    const emotionSpring = spring({
        frame: actionFrame,
        fps,
        config: { damping: 10, mass: 0.5, stiffness: 100 },
    });

    return (
        <div style={containerStyle}>
            {/* Background layer */}
            {data.bg_image_path && (
                <Background
                    imagePath={data.bg_image_path}
                    effect={data.camera_effect || "none"}
                    durationInFrames={durationInFrames}
                />
            )}

            {/* B-Roll layer */}
            {bRoll && (
                <div style={{
                    position: "absolute",
                    inset: 0,
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                    zIndex: 1,
                    opacity: interpolate(actionFrame, [0, 15], [0, 1], { extrapolateRight: "clamp" }),
                    transform: `translateY(${interpolate(actionFrame, [0, 15], [20, 0], { extrapolateRight: "clamp" })}px)`,
                }}>
                    <img src={staticFile(bRoll)} style={{ maxWidth: "80%", maxHeight: "70%", borderRadius: "20px", boxShadow: "0 20px 50px rgba(0,0,0,0.5)" }} />
                </div>
            )}

            {/* Stickman layer */}
            <div style={{ position: "absolute", inset: 0, zIndex: 2 }}>
                <Stickman
                    action={action}
                    actionFrame={actionFrame}
                    color="#FFFFFF"
                    accentColor="#3498db"
                    lineWidth={3}
                    scale={1.5}
                />

                {/* Emotion Icon */}
                {emotionIcon && (
                    <div style={{
                        position: "absolute",
                        bottom: "35%", // roughly above head
                        right: "13%", // roughly above head
                        fontSize: "60px",
                        transform: `scale(${emotionSpring})`,
                        filter: "drop-shadow(0 0 10px rgba(255,255,255,0.5))",
                    }}>
                        {mapEmotion(emotionIcon)}
                    </div>
                )}
            </div>

            {/* Subtitle layer */}
            <div style={{ zIndex: 3, position: "absolute", inset: 0, pointerEvents: "none" }}>
                <Subtitle
                    text={data.text}
                    durationInFrames={durationInFrames}
                />
            </div>

            {/* Audio layer */}
            {data.audio_path && (
                <Audio src={staticFile(data.audio_path)} />
            )}
        </div>
    );
};

/**
 * Map character_action / character_state to Stickman action prop.
 */
function mapAction(action: string): string {
    const mapping: Record<string, string> = {
        idle: "idle",
        wave: "wave",
        point: "point",
        pointing: "point",
        walk: "walk",
        walking: "walk",
        happy: "happy",
        sad: "sad",
        serious: "idle",
        tired: "sad",
        sitting: "sitting",
        counting: "counting",
        writing: "writing",
        fist_pump: "fist_pump",
        explain: "explain",
        none: "idle",
    };
    return mapping[action] || "idle";
}

function mapEmotion(icon: string): string {
    const mapping: Record<string, string> = {
        sweat: "😅",
        bulb: "💡",
        question: "❓",
        anger: "💢",
        heart: "❤️",
    };
    return mapping[icon] || "";
}
