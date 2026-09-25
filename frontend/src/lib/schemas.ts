import { z } from "zod";

export const TraceEventSchema = z.object({
  node: z.string(),
  output: z.record(z.string(), z.unknown()),
});

export type TraceEvent = z.infer<typeof TraceEventSchema>;

export type AskSkeletonResponse = {
  id: string;
  status: string;
};
