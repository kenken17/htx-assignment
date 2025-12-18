import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, fireEvent, screen } from "@testing-library/vue";

// 1) Mock the exports used by SearchPanel.vue
vi.mock("../src/api", () => ({
  search: vi.fn(async (_q: string, _topK: number) => ({
    results: [
      { media_type: "video", id: 1, filename: "video1.mp4", score: 0.9 },
      {
        media_type: "transcription",
        id: 10,
        filename: "audio1.wav",
        text: "hello",
        score: 0.8,
      },
    ],
  })),
  getVideos: vi.fn(async () => [{ id: 1, filename: "video1.mp4" }]),
  getTranscriptions: vi.fn(async () => [{ id: 10, filename: "audio1.wav" }]),
  searchByReference: vi.fn(
    async (_type: "video" | "transcription", _id: number, _topK: number) => ({
      results: [
        { media_type: "video", id: 2, filename: "video2.mp4", score: 0.95 },
        {
          media_type: "transcription",
          id: 11,
          filename: "audio2.wav",
          text: "world",
          score: 0.85,
        },
      ],
    }),
  ),
}));

const api = await import("../src/api");
const search = api.search as unknown as ReturnType<typeof vi.fn>;
const getVideos = api.getVideos as unknown as ReturnType<typeof vi.fn>;
const getTranscriptions = api.getTranscriptions as unknown as ReturnType<
  typeof vi.fn
>;
const searchByReference = api.searchByReference as unknown as ReturnType<
  typeof vi.fn
>;

function mockFetchJsonOnce(payload: any) {
  (globalThis.fetch as any).mockResolvedValueOnce({
    ok: true,
    json: async () => payload,
    text: async () => JSON.stringify(payload),
  });
}
describe("SearchPanel", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    globalThis.fetch = vi.fn();
  });

  it("runs text search and renders results (video + audio)", async () => {
    // 2) Import component after mocks are set
    const { default: SearchPanel } =
      await import("../src/components/SearchPanel.vue");
    render(SearchPanel);

    const input = screen.getByPlaceholderText(
      /search: objects, filenames, transcriptions/i,
    );
    await fireEvent.update(input, "car");

    await fireEvent.click(screen.getByRole("button", { name: /^search$/i }));

    expect(search).toHaveBeenCalledTimes(1);
    expect(search).toHaveBeenCalledWith("car", expect.any(Number));

    // UI renders results as JSON <pre>

    expect(
      await screen.findByText(/video1\.mp4/i, { selector: "pre" }),
    ).toBeInTheDocument();
    +expect(
      screen.getByText(/audio1\.wav/i, { selector: "pre" }),
    ).toBeInTheDocument();
  });

  it("supports cross-media search via reference selection", async () => {
    const { default: SearchPanel } =
      await import("../src/components/SearchPanel.vue");
    render(SearchPanel);

    // On mount it loads reference lists
    // Use waitFor to allow async onMounted logic to complete
    await vi.waitFor(() => {
      expect(getVideos).toHaveBeenCalledTimes(1);
      expect(getTranscriptions).toHaveBeenCalledTimes(1);
    });

    // Click a video reference -> this calls runSearch() immediately
    await fireEvent.click(
      await screen.findByRole("button", { name: /video1\.mp4/i }),
    );

    // 3) Wait until the ref search has actually happened
    await vi.waitFor(() => {
      expect(searchByReference).toHaveBeenCalledTimes(1);
    });

    expect(searchByReference).toHaveBeenCalledWith(
      "video",
      1,
      expect.any(Number),
    );

    // 4) Results swapped to mocked ref output
    expect(await screen.findByText(/video2\.mp4/i)).toBeInTheDocument();
    expect(screen.getByText(/audio2\.wav/i)).toBeInTheDocument();
  });
});
