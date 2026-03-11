import React from "react";
import { Composition, Series, getInputProps } from "remotion";
import { Scene } from "./components/Scene";
import { Thumbnail } from "./components/Thumbnail";

// Types
interface SceneData {
    scene_id: number;
    text: string;
    word_count: number;
    expected_duration: number;
    actual_duration: number;
    audio_path: string;
    bg_image_path?: string;
    bg_prompt: string;
    bg_seed: number;
    character_state?: string;
    character_action?: string;
    camera_effect?: string;
    visual_timeline?: Array<{
        time_offset: number;
        bg_prompt: string;
        action: string;
        b_roll?: string;
        emotion_icon?: string;
    }>;
    actions?: Array<{
        time_start: number;
        action: string;
        emotion_icon?: string;
        b_roll?: string
    }>;
}

interface ProjectData {
    meta?: {
        title?: string;
        video_id?: string;
    };
    project_name?: string;
    scenes: SceneData[];
    pipeline_result?: {
        total_actual_duration?: number;
    };
}

interface ThumbnailData {
    title: string;
    style?: string;
    width?: number;
    height?: number;
}

// Default props for studio preview
const defaultProps: ProjectData = {
    meta: { title: "Preview", video_id: "PREVIEW" },
    scenes: [
        {
            scene_id: 1,
            text: "Welcome to Stickman Factory. This is a preview scene.",
            word_count: 9,
            expected_duration: 4,
            actual_duration: 4,
            audio_path: "",
            bg_prompt: "Preview background",
            bg_seed: 42,
            character_state: "wave",
        },
    ],
};

const defaultThumbnailProps: ThumbnailData = {
    title: "Preview Title",
    style: "high_contrast",
    width: 1280,
    height: 720,
};

const FPS = 30;

/**
 * VideoRoot: Ghép nối tất cả scenes thành video hoàn chỉnh.
 * Sử dụng Remotion Series để xếp cảnh nối tiếp nhau.
 */
export const VideoComposition: React.FC<ProjectData> = (props) => {
    const scenes = props.scenes || [];
    const TRANSITION_FRAMES = 15;

    return (
        <Series>
            {scenes.map((scene, i) => {
                const duration = scene.actual_duration || scene.expected_duration || 5;
                const baseDurationInFrames = Math.ceil(duration * FPS);
                const isLast = i === scenes.length - 1;

                const offset = i === 0 ? 0 : -TRANSITION_FRAMES;
                const durationInFrames = baseDurationInFrames + (isLast ? 0 : TRANSITION_FRAMES);

                return (
                    <Series.Sequence
                        key={scene.scene_id}
                        durationInFrames={durationInFrames}
                        offset={offset}
                        name={`Scene_${scene.scene_id}`}
                    >
                        <Scene
                            data={scene}
                            durationInFrames={durationInFrames}
                            transitionFrames={isLast ? 0 : TRANSITION_FRAMES}
                        />
                    </Series.Sequence>
                );
            })}
        </Series>
    );
};

/**
 * ThumbnailComposition: Render ảnh thumbnail tĩnh.
 */
const ThumbnailComposition: React.FC<ThumbnailData> = (props) => {
    return <Thumbnail {...props} />;
};

/**
 * RemotionRoot: Đăng ký Composition cho Remotion CLI & Studio.
 */
export const RemotionRoot: React.FC = () => {
    // Determine props: Use getInputProps() if available, otherwise defaultProps
    const inputProps = getInputProps() as unknown as ProjectData;
    const finalProps = (inputProps && inputProps.scenes && inputProps.scenes.length > 0)
        ? inputProps
        : defaultProps;

    // Tính tổng duration dựa trên dynamic props
    const totalDuration = finalProps.scenes.reduce(
        (sum, s) => sum + (s.actual_duration || s.expected_duration || 5),
        0
    );
    const totalFrames = Math.max(1, Math.ceil(totalDuration * FPS));

    return (
        <>
            <Composition
                id="VideoRoot"
                component={VideoComposition as any}
                durationInFrames={totalFrames}
                fps={FPS}
                width={1920}
                height={1080}
                defaultProps={defaultProps as any}
            />
            <Composition
                id="ThumbnailComposition"
                component={ThumbnailComposition as any}
                durationInFrames={1}
                fps={FPS}
                width={1280}
                height={720}
                defaultProps={defaultThumbnailProps as any}
            />
        </>
    );
};
