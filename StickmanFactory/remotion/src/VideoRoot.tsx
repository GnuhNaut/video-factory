import React from "react";
import { Composition, Sequence } from "remotion";
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
    character_state: string;
    character_action?: string;
    camera_effect?: string;
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
 * Sử dụng Remotion Sequence để xếp cảnh nối tiếp nhau.
 */
const VideoComposition: React.FC<ProjectData> = (props) => {
    const scenes = props.scenes || [];

    // Tính from frame cho từng scene
    let currentFrame = 0;

    return (
        <>
            {scenes.map((scene, i) => {
                const duration = scene.actual_duration || scene.expected_duration || 5;
                const durationInFrames = Math.ceil(duration * FPS);
                const fromFrame = currentFrame;
                currentFrame += durationInFrames;

                return (
                    <Sequence
                        key={scene.scene_id}
                        from={fromFrame}
                        durationInFrames={durationInFrames}
                        name={`Scene ${scene.scene_id}`}
                    >
                        <Scene data={scene} durationInFrames={durationInFrames} />
                    </Sequence>
                );
            })}
        </>
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
    // Tính tổng duration
    const totalDuration = defaultProps.scenes.reduce(
        (sum, s) => sum + (s.actual_duration || s.expected_duration || 5),
        0
    );
    const totalFrames = Math.ceil(totalDuration * FPS);

    return (
        <>
            <Composition
                id="VideoRoot"
                component={VideoComposition}
                durationInFrames={totalFrames}
                fps={FPS}
                width={1920}
                height={1080}
                defaultProps={defaultProps}
            />
            <Composition
                id="ThumbnailComposition"
                component={ThumbnailComposition}
                durationInFrames={1}
                fps={FPS}
                width={1280}
                height={720}
                defaultProps={defaultThumbnailProps}
            />
        </>
    );
};
