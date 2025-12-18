import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, fireEvent, screen } from "@testing-library/vue";
import userEvent from "@testing-library/user-event";
import UploadPanel from "../src/components/UploadPanel.vue";
import { ref } from "vue";

vi.mock("../src/api", async () => {
  return {
    upload: vi.fn(async (_path: any, _file: any) => ({ job_id: "job-1" })),
  };
});

// Keep UploadPanel stable by mocking useJob (no polling / timers)
vi.mock("../src/useJob", async () => {
  return {
    useJob: () => ({
      job: ref(null),
      result: ref(null),
      error: ref(null),
    }),
  };
});

const { upload } = await import("../src/api");

function makeFile(name: string, type: string) {
  return new File(["dummy"], name, { type });
}

describe("UploadPanel", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("uploads video files to /process/video", async () => {
    render(UploadPanel);

    // default is video
    const input = screen.getByLabelText(
      /select file\(s\)/i,
    ) as HTMLInputElement;
    const file = makeFile("clip.mp4", "video/mp4");
    const user = userEvent.setup();
    await user.upload(input, file);

    await fireEvent.click(screen.getByRole("button", { name: /submit/i }));

    expect(upload).toHaveBeenCalledTimes(1);
    expect(upload).toHaveBeenCalledWith("/process/video", file);
  });

  it("uploads audio files to /process/audio when processing type is audio", async () => {
    render(UploadPanel);

    // switch to audio
    await fireEvent.update(screen.getByLabelText(/processing type/i), "audio");

    const input = screen.getByLabelText(
      /select file\(s\)/i,
    ) as HTMLInputElement;
    const file = makeFile("speech.wav", "audio/wav");
    const user = userEvent.setup();
    await user.upload(input, file);

    await fireEvent.click(screen.getByRole("button", { name: /submit/i }));

    expect(upload).toHaveBeenCalledTimes(1);
    expect(upload).toHaveBeenCalledWith("/process/audio", file);
  });
});
