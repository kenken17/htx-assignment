import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/vue";
import ResultViewer from "../src/components/viewers/ResultViewer.vue";
import { within } from "@testing-library/dom";

describe("ResultViewer", () => {
  it("renders video object detection results", async () => {
    render(ResultViewer, {
      props: {
        result: {
          summary: "A short summary",
          objects: [
            { label: "person", confidence: 0.92 },
            { label: "car", confidence: 0.81 },
          ],
          keyframes: [{ time_s: 0.0, frame_idx: 0 }],
        },
      },
    });

    const det = await screen.findByTestId("video-detections");

    expect(within(det).getAllByText(/person/i).length).toBeGreaterThan(0);
    expect(within(det).getAllByText(/car/i).length).toBeGreaterThan(0);
  });

  it("renders audio transcription and segments", async () => {
    render(ResultViewer, {
      props: {
        result: {
          text: "hello world",
          segments: [
            { start: 0.0, end: 1.2, text: "hello" },
            { start: 1.2, end: 2.4, text: "world" },
          ],
        },
      },
    });

    const det = await screen.findByTestId("video-detections");

    expect(within(det).getAllByText(/hello world/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/transcription/i)).toBeInTheDocument();
    expect(screen.getByText(/\"start\": 0/i)).toBeInTheDocument();
    expect(screen.getByText(/\"end\": 2\.4/i)).toBeInTheDocument();
  });
});
