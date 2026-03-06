import React from "react";
import { Audio, useVideoConfig, staticFile, useCurrentFrame } from "remotion";
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
    actions?: Array<{ time_start: number; action: string }>;
    camera_effect?: string;
    actual_duration?: number;
    expected_duration?: number;
}

interface SceneProps {
    data: SceneData;
    durationInFrames: number;
}

export const Scene: React.FC<SceneProps> = ({ data, durationInFrames }) => {
    const { fps } = useVideoConfig();
    const frame = useCurrentFrame();

    // Determine stickman action based on timeline
    let action = "idle";
    let actionFrame = frame;

    if (data.actions && data.actions.length > 0) {
        const currentTime = frame / fps;
        let activeActionObj = data.actions[0];

        for (const act of data.actions) {
            if (act.time_start <= currentTime) {
                activeActionObj = act;
            }
        }

        action = mapAction(activeActionObj.action);
        const actionStartFrame = Math.round(activeActionObj.time_start * fps);
        actionFrame = Math.max(0, frame - actionStartFrame);
    } else {
        // Fallback for older JSONs
        action = data.character_action && data.character_action !== "none"
            ? mapAction(data.character_action)
            : data.character_state ? mapAction(data.character_state) : "idle";
    }

    const containerStyle: React.CSSProperties = {
        position: "relative",
        width: "100%",
        height: "100%",
        overflow: "hidden",
        backgroundColor: "#1a1a2e",
    };

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

            {/* Stickman layer */}
            <Stickman
                action={action}
                actionFrame={actionFrame}
                color="#FFFFFF"
                accentColor="#3498db"
                lineWidth={3}
                scale={1.5}
            />

            {/* Subtitle layer */}
            <Subtitle
                text={data.text}
                durationInFrames={durationInFrames}
            />

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
        sitting: "idle",
        counting: "point",
        writing: "point",
        fist_pump: "happy",
        none: "idle",
    };
    return mapping[action] || "idle";
}
