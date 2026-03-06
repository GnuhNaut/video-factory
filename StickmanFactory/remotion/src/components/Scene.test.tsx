import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { Scene } from './Scene';
import React from 'react';

// Mock component dependencies
vi.mock('./Subtitle', () => ({
    Subtitle: ({ durationInFrames }: { durationInFrames: number }) => (
        <div data-testid="mock-subtitle" data-duration={durationInFrames}></div>
    )
}));
vi.mock('./Background', () => ({
    Background: ({ durationInFrames }: { durationInFrames: number }) => (
        <div data-testid="mock-background" data-duration={durationInFrames}></div>
    )
}));
vi.mock('./Stickman', () => ({
    Stickman: () => <div data-testid="mock-stickman"></div>
}));

// Mock remotion environment
vi.mock('remotion', () => ({
    useCurrentFrame: () => 0,
    useVideoConfig: () => ({ fps: 30 }),
    interpolate: () => 1,
    spring: () => 1,
    staticFile: (path: string) => path,
    Audio: ({ src }: { src: string }) => <audio src={src} data-testid="mock-audio" />
}));

describe('Scene Component', () => {
    it('passes down the correct durationInFrames and data seamlessly', () => {
        // Mock dữ liệu đầu vào chuẩn xác giống JSON
        const mockSceneData = {
            scene_id: 1,
            text: "Xin chào các bạn",
            audio_path: "audio/test.wav",
            bg_image_path: "bg/test.png",
            character_state: "idle",
            character_action: "wave",
            camera_effect: "zoom_in",
            actual_duration: 5.0,
            expected_duration: 5.0
        };

        // duration 5.0s * 30fps = 150 frames
        const durationInFrames = 150;

        const { getByTestId, queryByTestId } = render(
            <Scene data={mockSceneData} durationInFrames={durationInFrames} />
        );

        // Xác minh Subtitle nhận đúng durationInFrames 150 để render
        const subtitleMatch = getByTestId('mock-subtitle');
        expect(subtitleMatch.getAttribute('data-duration')).toBe('150');

        // Xác minh Background nhận đúng durationInFrames 150
        const bgMatch = getByTestId('mock-background');
        expect(bgMatch.getAttribute('data-duration')).toBe('150');

        // Xác minh Audio render path đúng
        const audioMatch = getByTestId('mock-audio');
        expect(audioMatch).toBeTruthy();
        expect(audioMatch.getAttribute('src')).toBe('audio/test.wav');
    });
});
