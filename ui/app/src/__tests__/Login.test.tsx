import { test, expect, beforeAll, afterAll, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { loginForm, fillOutLoginForm } from './utils';
import App from '../App';


const server = setupServer(
  http.post('http://localhost:8000/api/v1/auth/login/', () => {
    return HttpResponse.json({
      token_type: 'Bearer',
      access_token: 'access_token',
      access_token_expires_at: '2023-12-06T00:51:14.322Z',
      refresh_token: 'refresh_token',
      refresh_token_expires_at: '2023-12-06T00:51:14.322Z',
    });
  }),
  http.get('http://localhost:8000/api/v1/todo/list/', () => {
    return HttpResponse.json([]);
  }),
  http.get('http://localhost:8000/api/v1/todo/task/', () => {
    return HttpResponse.json([]);
  }),
);


beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());


function initializeLoginPage() {
  const user = userEvent.setup();
  render(<App />);
  return user;
}


test('has login page', () => {
  initializeLoginPage();

  const pageTitle = screen.getByRole('heading', { level: 2 });

  expect(pageTitle).toHaveTextContent(/Login/);
});


test('has required form fields', () => {
  initializeLoginPage();

  const form = loginForm();

  expect(form.usernameField).toBeInvalid();
  expect(form.passwordField).toBeInvalid();
  expect(form.loginButton).toBeDisabled();
});


test('can submit after supplying username and password', async () => {
  const user = initializeLoginPage();

  const form = loginForm();
  await fillOutLoginForm(user, form);

  expect(form.usernameField).toBeValid();
  expect(form.passwordField).toBeValid();
  expect(form.loginButton).toBeEnabled();
});


test('can login to app with valid username and password', async () => {
  const user = initializeLoginPage();

  const form = loginForm();
  await fillOutLoginForm(user, form);
  await user.click(form.loginButton);

  const pageTitle = screen.getByRole('heading', { level: 2 });

  expect(pageTitle).toHaveTextContent(/Todos/);
});


test('can see error with backend issue from message response', async () => {
  server.use(
    http.post('http://localhost:8000/api/v1/auth/login/', () => {
      return HttpResponse.json(
        { message: 'Invalid credentials provided', },
        { status: 401, },
      );
    }),
  );
  const user = initializeLoginPage();

  const form = loginForm();
  await fillOutLoginForm(user, form);
  await user.click(form.loginButton);

  const pageTitle = screen.getByRole('heading', { level: 2 });
  const alert = screen.getByRole('alert');

  expect(pageTitle).toHaveTextContent(/Login/);
  expect(alert).toHaveTextContent(/Issue occurred during request: Invalid credentials provided/);
});


test('can see error with api call', async () => {
  server.use(
    http.post('http://localhost:8000/api/v1/auth/login/', () => {
      return HttpResponse.error();
    }),
  );
  const user = initializeLoginPage();

  const form = loginForm();
  await fillOutLoginForm(user, form);
  await user.click(form.loginButton);

  const pageTitle = screen.getByRole('heading', { level: 2 });
  const alert = screen.getByRole('alert');

  expect(pageTitle).toHaveTextContent(/Login/);
  expect(alert).toHaveTextContent(/Error occurred during login./);
});


test('can go to register page from login', async () => {
  initializeLoginPage();

  const registerLink = screen.getByRole('link', { name: 'Register' });

  expect(registerLink).toHaveAttribute('href', '#register');
});
