import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { Stickman } from './Stickman';
import React from 'react';

// Mock remotion functions that rely on video context
vi.mock('remotion', () => ({
    useCurrentFrame: () => 0,
    useVideoConfig: () => ({ fps: 30 }),
    interpolate: () => 1,
    spring: () => 1,
}));

describe('Stickman Component', () => {
    it('renders correctly with idle action', () => {
        const { container } = render(<Stickman action="idle" scale={1} />);

        // In idle mode, the right arm should be pointing down resting
        // L150,165 is the coordinate for resting arm in Stickman.tsx
        const elements = container.querySelectorAll('path');
        const rightArmPath = Array.from(elements).find(el => el.getAttribute('d')?.includes('L150,165'));

        expect(rightArmPath).toBeTruthy();
        expect(rightArmPath?.getAttribute('d')).toContain('M140,95 L150,165');
    });

    it('renders correctly with wave action', () => {
        const { container } = render(<Stickman action="wave" scale={1} />);

        // In wave mode, the right arm should point to elbow then hand up
        // L155,60 is elbow
        const elements = container.querySelectorAll('path');
        const rightArmPath = Array.from(elements).find(el => el.getAttribute('d')?.includes('L155,60'));

        expect(rightArmPath).toBeTruthy();
        expect(rightArmPath?.getAttribute('d')).toContain('M140,95 L155,60');
    });
});
