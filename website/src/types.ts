export type Certification = {
  name: string;
  year?: number | null;
  issuer?: string | null;
};

export type Education = {
  institution: string;
  degree?: string | null;
  field?: string | null;
  start_year?: number | null;
  end_year?: number | null;
};

export type Experience = {
  company: string;
  title?: string | null;
  start?: string | null;
  end?: string | null;
  description?: string | null;
};

export type Link = {
  type?: "linkedin" | "github" | "portfolio" | "other";
  url: string;
};

export type CandidateProfile = {
  full_name?: string | null;
  email?: string | null;
  phone?: string | null;
  location?: string | null;
  links: Link[];
  summary?: string | null;
  skills: string[];
  education: Education[];
  experience: Experience[];
  certifications?: Certification[] | null;
};

export type Snippet = {
  text: string;
  metadata: {
    section?: string | null;
    candidate_id?: string | null;
    candidate_name?: string | null;
    company?: string | null;
    institution?: string | null;
    source_file?: string | null;
  };
  score?: {
    distance?: number | null;
    similarity?: number | null;
  };
};

export type AskResponse = {
  sections: string[];
  facts: CandidateProfile[];
  docs: CandidateProfile[];
  answer?: string;
  why?: string;
};

export type HistoryItem = {
  id: string;
  question: string;
  timestamp: number;
  response?: AskResponse;
};
