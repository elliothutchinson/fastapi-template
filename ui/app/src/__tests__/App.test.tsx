import { test, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from '../App';


test('renders the app', () => {
  render(<App />);

  const appTitle = screen.getByRole('heading', { level: 1 });

  expect(appTitle).toHaveTextContent(/Todos App/);
});
