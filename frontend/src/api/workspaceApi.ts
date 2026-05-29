import { z } from 'zod';
import { INITIAL_DOMAINS, INITIAL_WORKFLOWS, INITIAL_ARTIFACTS } from '../stores/mockData';

// --- Zod Schemas (Intent: Type safety for Python/Go backend migration) ---

export const ResourceSchema = z.object({
  id: z.string(),
  name: z.string(),
  lines: z.number(),
  fileType: z.string(),
});

export const TopicSchema = z.object({
  id: z.string(),
  name: z.string(),
  lastMessage: z.string().optional(),
  pinned: z.boolean().optional(),
  archived: z.boolean().optional(),
});

export const ChapterSchema = z.object({
  id: z.string(),
  name: z.string(),
  topics: z.array(TopicSchema),
  pinned: z.boolean().optional(),
  archived: z.boolean().optional(),
  description: z.string().optional(),
  instructions: z.string().optional(),
  memory: z.string().optional(),
});

export const SubjectSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string().optional(),
  chapters: z.array(ChapterSchema),
  resources: z.array(ResourceSchema),
  instructions: z.string().optional(),
  memory: z.string().optional(),
  pinned: z.boolean().optional(),
  archived: z.boolean().optional(),
});

export const DomainSchema = z.object({
  id: z.string(),
  name: z.string(),
  subjects: z.array(SubjectSchema),
  pinned: z.boolean().optional(),
  archived: z.boolean().optional(),
});

export type DomainDTO = z.infer<typeof DomainSchema>;
export type SubjectDTO = z.infer<typeof SubjectSchema>;
export type ChapterDTO = z.infer<typeof ChapterSchema>;
export type TopicDTO = z.infer<typeof TopicSchema>;

// --- Mock API Fetchers ---

// In the future, these will use fetch/axios pointing to your Python/Go backend.
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const api = {
  getDomains: async (): Promise<DomainDTO[]> => {
    await delay(300); // Simulate network
    const data = INITIAL_DOMAINS; // Local storage or API fetch goes here
    return z.array(DomainSchema).parse(data);
  },

  getDomain: async (domainId: string): Promise<DomainDTO> => {
    await delay(300);
    const domain = INITIAL_DOMAINS.find(d => d.id === domainId);
    if (!domain) throw new Error('Domain not found');
    return DomainSchema.parse(domain);
  },

  getSubject: async (domainId: string, subjectId: string): Promise<SubjectDTO> => {
    await delay(300);
    const domain = INITIAL_DOMAINS.find(d => d.id === domainId);
    const subject = domain?.subjects.find(s => s.id === subjectId);
    if (!subject) throw new Error('Subject not found');
    return SubjectSchema.parse(subject);
  },

  getChapter: async (domainId: string, subjectId: string, chapterId: string): Promise<ChapterDTO> => {
    await delay(300);
    const domain = INITIAL_DOMAINS.find(d => d.id === domainId);
    const subject = domain?.subjects.find(s => s.id === subjectId);
    const chapter = subject?.chapters.find(c => c.id === chapterId);
    if (!chapter) throw new Error('Chapter not found');
    return ChapterSchema.parse(chapter);
  },

  getTopic: async (domainId: string, subjectId: string, chapterId: string, topicId: string): Promise<TopicDTO> => {
    await delay(300);
    const domain = INITIAL_DOMAINS.find(d => d.id === domainId);
    const subject = domain?.subjects.find(s => s.id === subjectId);
    const chapter = subject?.chapters.find(c => c.id === chapterId);
    const topic = chapter?.topics.find(t => t.id === topicId);
    if (!topic) throw new Error('Topic not found');
    return TopicSchema.parse(topic);
  }
};
