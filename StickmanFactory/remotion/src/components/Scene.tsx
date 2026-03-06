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
    visual_timeline?: Array<{
        time_offset: number;
        bg_prompt: string;
        action: string;
        emotion_icon?: string;
        b_roll?: string;
        b_roll_path?: string;
    }>;
    actions?: Array<{
        time_start: number;
        action: string;
        emotion_icon?: string;
        b_roll?: string;
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
    let previousAction = "idle";
    let actionFrame = frame;
    let emotionIcon = "";
    let bRoll = "";

    const timeline = data.visual_timeline || data.actions || [];

    if (timeline.length > 0) {
        const currentTime = frame / fps;
        let activeIndex = 0;

        for (let i = 0; i < timeline.length; i++) {
            const item = timeline[i] as any;
            const timeStart = item.time_offset !== undefined ? item.time_offset : item.time_start;
            if (timeStart <= currentTime) {
                activeIndex = i;
            }
        }

        const activeActionObj = timeline[activeIndex] as any;
        action = mapAction(activeActionObj.action);
        emotionIcon = activeActionObj.emotion_icon || "";
        bRoll = activeActionObj.b_roll_path || activeActionObj.b_roll || "";

        const timeStart = activeActionObj.time_offset !== undefined ? activeActionObj.time_offset : activeActionObj.time_start;
        const actionStartFrame = Math.round(timeStart * fps);
        actionFrame = Math.max(0, frame - actionStartFrame);

        if (activeIndex > 0) {
            const prevActionObj = timeline[activeIndex - 1] as any;
            previousAction = mapAction(prevActionObj.action);
        } else {
            previousAction = action;
        }
    } else {
        // Fallback for older JSONs
        action = data.character_action && data.character_action !== "none"
            ? mapAction(data.character_action)
            : data.character_state ? mapAction(data.character_state) : "idle";
        previousAction = action;
    }

    // Smooth transition fade in/out
    const opacity = transitionFrames > 0
        ? interpolate(
            frame,
            [0, transitionFrames, durationInFrames - transitionFrames, durationInFrames],
            [0, 1, 1, 0],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        )
        : 1;

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

    // Prepare background timeline
    let bgTimeline: Array<{ time_offset: number; bg_image_path?: string; camera_effect?: string }> = [];
    if (data.visual_timeline && data.visual_timeline.length > 0) {
        bgTimeline = data.visual_timeline.map(item => ({
            time_offset: item.time_offset,
            bg_image_path: item.bg_prompt ? data.bg_image_path : undefined, // Handled correctly in orchestrator/Background
            camera_effect: data.camera_effect
        }));
    } else if (data.bg_image_path) {
        bgTimeline = [{
            time_offset: 0,
            bg_image_path: data.bg_image_path,
            camera_effect: data.camera_effect
        }];
    }

    // Horizontal movement sync for character group
    const isMoving = action === "walk" || action === "walking" || action === "run";
    const moveTranslate = isMoving
        ? interpolate(actionFrame, [0, 90], [50, -50], { extrapolateRight: "clamp" })
        : 0;

    return (
        <div style={containerStyle}>
            {/* Background layer (zIndex default 0) */}
            {bgTimeline.length > 0 && (
                <Background
                    timeline={bgTimeline}
                    durationInFrames={durationInFrames}
                />
            )}

            {/* B-Roll layer (zIndex 1) */}
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
                    <img src={staticFile(bRoll)} style={{
                        maxWidth: "80%",
                        maxHeight: "75%",
                        objectFit: "cover",
                        borderRadius: "20px",
                        boxShadow: "0 20px 50px rgba(0,0,0,0.5)",
                        border: "5px solid white"
                    }} />
                </div>
            )}

            {/* Character layer Group (Stickman + Emotion) (zIndex 2) */}
            <div style={{ position: "absolute", inset: 0, zIndex: 2 }}>
                <Stickman
                    action={action}
                    previousAction={previousAction}
                    actionFrame={actionFrame}
                    color="#FFFFFF"
                    accentColor="#3498db"
                    lineWidth={3}
                    scale={1.5}
                />

                {/* Emotion Icon (Synced with Stickman movement) */}
                {emotionIcon && (
                    <div style={{
                        position: "absolute",
                        bottom: action === "sitting" ? "30%" : "35%",
                        right: `${10 + moveTranslate + 3}%`, // Offset from stickman's side
                        fontSize: "60px",
                        transform: `scale(${emotionSpring})`,
                        filter: "drop-shadow(0 0 10px rgba(255,255,255,0.5))",
                    }}>
                        {mapEmotion(emotionIcon)}
                    </div>
                )}
            </div>

            {/* Subtitle layer (zIndex 3) */}
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
        run: "run",
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
        sad: "💧",
        happy: "😊"
    };
    return mapping[icon] || "";
}
