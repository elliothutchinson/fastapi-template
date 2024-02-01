import { test, expect, beforeAll, afterAll, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import App from '../App';


const server = setupServer(
  http.post('http://localhost:8000/api/v1/user/', () => {
    return HttpResponse.json({
      username: 'jojo',
      first_name: 'joseph',
      last_name: 'joestar',
      email: 'jojo@example.com',
      verified_email: null,
      roles: ["USER"],
      disabled: false,
      date_created: "2023-12-07T01:22:06.834Z",
      date_modified: null,
      last_login: null,
    });
  }),
);


beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());


async function navigateRegisterPage(user) {
  const registerLink = screen.getByRole('link', { name: 'Register' });
  await user.click(registerLink);
}


async function initializeRegisterPage() {
  const user = userEvent.setup();
  render(<App />);
  await navigateRegisterPage(user);
  return user;
}


function registrationForm() {
  const usernameField = screen.getByLabelText(/Username/);
  const firstNameField = screen.getByLabelText(/First Name/);
  const lastNameField = screen.getByLabelText(/Last Name/);
  const emailField = screen.getByLabelText(/Email/);
  const passwordField = screen.getByLabelText(/^Password/);
  const confirmPasswordField = screen.getByLabelText(/Confirm Password/);
  const registerButton = screen.getByRole('button', { name: 'Register' });

  return {
    usernameField,
    firstNameField,
    lastNameField,
    emailField,
    passwordField,
    confirmPasswordField,
    registerButton,
  }
}


async function fillOutRegistrationForm(user, form) {
  await user.type(form.usernameField, 'jojo');
  await user.type(form.firstNameField, 'joseph');
  await user.type(form.lastNameField, 'joestar');
  await user.type(form.emailField, 'jojo@example.com');
  await user.type(form.passwordField, 'password');
  await user.type(form.confirmPasswordField, 'password');
}


test('has register page', async () => {
  await initializeRegisterPage();

  const pageTitle = screen.getByRole('heading', { level: 2 });

  expect(pageTitle).toHaveTextContent(/Register/);
});


test('has required form fields', async () => {
  await initializeRegisterPage();

  const form = registrationForm();

  expect(form.usernameField).toBeInvalid();
  expect(form.firstNameField).toBeInvalid();
  expect(form.lastNameField).toBeInvalid();
  expect(form.emailField).toBeInvalid();
  expect(form.passwordField).toBeInvalid();
  expect(form.confirmPasswordField).toBeInvalid();
  expect(form.registerButton).toBeDisabled();
});


test('can submit after supplying form fields', async () => {
  const user = await initializeRegisterPage();

  const form = registrationForm();
  await fillOutRegistrationForm(user, form);

  expect(form.usernameField).toBeValid();
  expect(form.firstNameField).toBeValid();
  expect(form.lastNameField).toBeValid();
  expect(form.emailField).toBeValid();
  expect(form.passwordField).toBeValid();
  expect(form.confirmPasswordField).toBeValid();
  expect(form.registerButton).toBeEnabled();
});


test('taken to login page after successful registration', async () => {
  const user = await initializeRegisterPage();

  const form = registrationForm();
  await fillOutRegistrationForm(user, form);
  await user.click(form.registerButton);

  const pageTitle = screen.getByRole('heading', { level: 2 });
  const alert = screen.getByRole('alert');

  expect(pageTitle).toHaveTextContent(/Login/);
  expect(alert).toHaveTextContent(/User registered successfully/);
});


test('can see error with backend issue from request', async () => {
  server.use(
    http.post('http://localhost:8000/api/v1/user/', () => {
      return HttpResponse.json(
        {
          detail:[
            {
              loc: ['body','username'],
              msg: 'ensure this value has at least 4 characters',
              type: 'value_error.any_str.min_length',
              ctx: { limit_value: 4 },
            }
          ]
        },
        { status: 422, },
      );
    }),
  );
  const user = await initializeRegisterPage();

  const form = registrationForm();
  await fillOutRegistrationForm(user, form);
  await user.click(form.registerButton);

  const pageTitle = screen.getByRole('heading', { level: 2 });
  const alert = screen.getByRole('alert');

  expect(pageTitle).toHaveTextContent(/Register/);
  expect(alert).toHaveTextContent(/username: ensure this value has at least 4 characters/);
});


test('can see error with api call', async () => {
  server.use(
    http.post('http://localhost:8000/api/v1/user/', () => {
      return HttpResponse.error();
    }),
  );
  const user = await initializeRegisterPage();

  const form = registrationForm();
  await fillOutRegistrationForm(user, form);
  await user.click(form.registerButton);

  const pageTitle = screen.getByRole('heading', { level: 2 });
  const alert = screen.getByRole('alert');

  expect(pageTitle).toHaveTextContent(/Register/);
  expect(alert).toHaveTextContent(/Error occurred during registration./);
});


test('can go to login page from register', async () => {
  await initializeRegisterPage();

  const loginLink = screen.getByRole('link', { name: 'Login' });

  expect(loginLink).toHaveAttribute('href', '#login');
});
