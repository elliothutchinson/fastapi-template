import { test, expect, beforeAll, afterAll, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { loginForm, fillOutLoginForm } from './utils';
import App from '../App';


// todo: impl
test('has profile page', async () => {
  const user = userEvent.setup();
  render(<App />);
  // await navigateProfilePage(user);

  const pageTitle = screen.getByRole('heading', { level: 2 });

  // expect(pageTitle).toHaveTextContent(/Profile - View/);
});

// todo: mobile nav tests
// todo: navigate to todos
// todo: navigate to profile
// todo: navigate to logout
