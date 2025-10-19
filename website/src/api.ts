import { AskResponse } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

const MOCK_RESPONSE: AskResponse = {
  ok: true,
  sections: ['skills', 'experience'],
  facts: [
    {
      full_name: 'Amanda Lawrence',
      email: 'amanda.lawrence@email.com',
      phone: '555-0123',
      location: 'San Francisco, CA',
      links: [
        { type: 'linkedin', url: 'https://linkedin.com/in/amandal' },
        { type: 'github', url: 'https://github.com/amandal' },
      ],
      summary: 'Senior software engineer with 8+ years of experience in full-stack development.',
      skills: ['React', 'Python', 'TypeScript', 'Node.js', 'PostgreSQL', 'AWS', 'Docker', 'GraphQL', 'REST APIs', 'CI/CD'],
      education: [
        {
          institution: 'Stanford University',
          degree: 'Bachelor of Science',
          field: 'Computer Science',
          start_year: 2011,
          end_year: 2015,
        },
      ],
      experience: [
        {
          company: 'Tech Innovations LLC',
          title: 'Senior Software Engineer',
          start: '2020-01',
          end: 'Present',
          description: 'Led development of React-based web applications with Python backends.',
        },
        {
          company: 'StartupXYZ',
          title: 'Full Stack Developer',
          start: '2017-06',
          end: '2019-12',
          description: 'Built and maintained multiple microservices using Python and React.',
        },
      ],
      certifications: [
        { name: 'AWS Certified Solutions Architect', year: 2021, issuer: 'Amazon Web Services' },
      ],
    },
  ],
  docs: [
    {
      text: 'Led development of React-based web applications with Python backends. Implemented responsive UI components using modern React patterns and hooks. Built REST APIs and GraphQL endpoints using Python/FastAPI.',
      metadata: {
        section: 'experience',
        candidate_id: '123e4567-e89b-12d3-a456-426614174000',
        candidate_name: 'Amanda Lawrence',
        company: 'Tech Innovations LLC',
        institution: null,
        source_file: 'data/pdf/Amanda_Lawrence.pdf',
      },
      score: {
        distance: 0.14,
        similarity: 0.86,
      },
    },
    {
      text: 'Technical Skills: React, Python, TypeScript, Node.js, PostgreSQL, AWS, Docker, GraphQL, REST APIs, CI/CD, Jest, Pytest, Git',
      metadata: {
        section: 'skills',
        candidate_id: '123e4567-e89b-12d3-a456-426614174000',
        candidate_name: 'Amanda Lawrence',
        company: null,
        institution: null,
        source_file: 'data/pdf/Amanda_Lawrence.pdf',
      },
      score: {
        distance: 0.18,
        similarity: 0.82,
      },
    },
  ],
  answer: '**Amanda Lawrence** has extensive experience with both React and Python. She has worked as a Senior Software Engineer at Tech Innovations LLC since 2020, where she led development of React-based web applications with Python backends. Her skill set includes React, Python, TypeScript, and related technologies. She previously worked at StartupXYZ building microservices using Python and React.',
};

export async function askQuestion(
  question: string,
  skillLogic: 'and' | 'or' = 'and'
): Promise<AskResponse> {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 800));
    return MOCK_RESPONSE;
  }

  const response = await fetch(`${API_BASE_URL}/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question,
      skill_logic: skillLogic,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  const data: AskResponse = await response.json();

  return data;
}
