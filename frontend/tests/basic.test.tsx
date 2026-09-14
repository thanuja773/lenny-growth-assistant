import { render, screen } from '@testing-library/react';
import { EmptyState } from '../src/components/chat/EmptyState';
import { Composer } from '../src/components/chat/Composer';

describe('Frontend UI Tests', () => {
  it('renders EmptyState correctly', () => {
    render(<EmptyState onPromptSelect={() => {}} />);
    expect(screen.getByText('Lenny Growth Assistant')).toBeDefined();
    expect(screen.getByText('What makes a great growth team?')).toBeDefined();
  });

  it('renders Composer correctly', () => {
    render(<Composer onSend={() => {}} disabled={false} />);
    expect(screen.getByPlaceholderText("Ask Lenny's Growth Assistant anything...")).toBeDefined();
  });
});
