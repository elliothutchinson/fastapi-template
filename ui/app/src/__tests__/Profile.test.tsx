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
  http.get('http://localhost:8000/api/v1/user/', () => {
    return HttpResponse.json({
      username: 'jojo',
      first_name: 'joseph',
      last_name: 'joestar',
      email: 'jojo@example.com',
      verified_email: null,
      roles: ['USER'],
      disabled: false,
      date_created: '2023-12-07T01:22:06.834Z',
      date_modified: '2023-12-08T01:22:06.834Z',
      last_login: '2023-12-09T01:22:06.834Z',
    });
  }),
  http.put('http://localhost:8000/api/v1/user/', () => {
    return HttpResponse.json({
      username: 'jojo',
      first_name: 'Joseph',
      last_name: 'Joestar',
      email: 'jojostar@example.com',
      verified_email: null,
      roles: ['USER'],
      disabled: false,
      date_created: '2023-12-07T01:22:06.834Z',
      date_modified: '2023-12-08T01:22:06.834Z',
      last_login: '2023-12-09T01:22:06.834Z',
    });
  }),
);


beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());


async function navigateProfilePage(user) {
  const form = loginForm();
  await fillOutLoginForm(user, form);
  await user.click(form.loginButton);

  const profileLink = screen.getByRole('link', { name: 'jojo' });
  await user.click(profileLink);
}


async function navigateProfileEdit(user) {
  const editLink = screen.getByRole('link', { name: 'Edit' });
  await user.click(editLink);
}


async function initializeProfilePage() {
  const user = userEvent.setup();
  render(<App />);
  await navigateProfilePage(user);
  return user;
}


async function initializeProfileEdit() {
  const user = await initializeProfilePage();
  await navigateProfileEdit(user);
  return user;
}


function profileForm() {
  const firstNameField = screen.getByLabelText(/First Name/);
  const lastNameField = screen.getByLabelText(/Last Name/);
  const emailField = screen.getByLabelText(/Email/);

  return {
    firstNameField,
    lastNameField,
    emailField,
  }
}


function profileEditForm() {
  const form = profileForm();
  const updateButton = screen.getByRole('button', { name: 'Update' });

  return {
    ...form,
    updateButton,
  }
}


async function fillOutProfileEditForm(user, form) {
  await user.clear(form.firstNameField);
  await user.type(form.firstNameField, 'Joseph');

  await user.clear(form.lastNameField);
  await user.type(form.lastNameField, 'Joestar');

  await user.clear(form.emailField);
  await user.type(form.emailField, 'jojostar@example.com');
}


function changePasswordForm() {
  const passwordField = screen.getByLabelText(/^Password/);
  const confirmPasswordField = screen.getByLabelText(/Confirm Password/);
  const changePasswordButton = screen.getByRole('button', { name: 'Change Password' });

  return {
    passwordField,
    confirmPasswordField,
    changePasswordButton,
  }
}


async function fillOutChangePasswordForm(user, form) {
  await user.type(form.passwordField, 'password');
  await user.type(form.confirmPasswordField, 'password');
}


test('has view profile page', async () => {
  await initializeProfilePage();

  const pageTitle = screen.getByRole('heading', { level: 2 });

  expect(pageTitle).toHaveTextContent(/Profile - View/);
});


test('can view profile data', async () => {
  await initializeProfilePage();

  const form = profileForm();

  expect(form.firstNameField).toHaveAttribute('readonly');
  expect(form.firstNameField).toHaveValue('joseph');

  expect(form.lastNameField).toHaveAttribute('readonly');
  expect(form.lastNameField).toHaveValue('joestar');

  expect(form.emailField).toHaveAttribute('readonly');
  expect(form.emailField).toHaveValue('jojo@example.com');
});


test('has edit profile', async () => {
  await initializeProfileEdit();

  const pageTitles = screen.getAllByRole('heading', { level: 2 });

  expect(pageTitles[0]).toHaveTextContent(/Profile - Edit/);
});


test('has current profile data populated in edit profile form', async () => {
  await initializeProfileEdit();

  const form = profileEditForm();

  expect(form.firstNameField).toHaveValue('joseph');
  expect(form.lastNameField).toHaveValue('joestar');
  expect(form.emailField).toHaveValue('jojo@example.com');
});


test('edit profile form has required fields', async () => {
  const user = await initializeProfileEdit();

  const form = profileEditForm();

  await user.clear(form.firstNameField);
  await user.clear(form.lastNameField);
  await user.clear(form.emailField);

  expect(form.firstNameField).toBeInvalid();
  expect(form.lastNameField).toBeInvalid();
  expect(form.emailField).toBeInvalid();
  expect(form.updateButton).toBeDisabled();
});


test('can submit edit profile form', async () => {
  const user = await initializeProfileEdit();

  const form = profileEditForm();
  await fillOutProfileEditForm(user, form);

  expect(form.firstNameField).toHaveValue('Joseph');
  expect(form.lastNameField).toHaveValue('Joestar');
  expect(form.emailField).toHaveValue('jojostar@example.com');
  expect(form.updateButton).toBeEnabled();
});


test('taken to profile edit after successful profile update', async () => {
  const user = await initializeProfileEdit();

  const form = profileEditForm();
  await fillOutProfileEditForm(user, form);
  await user.click(form.updateButton);

  const pageTitles = screen.getAllByRole('heading', { level: 2 });
  const alert = screen.getByRole('alert');

  expect(pageTitles[0]).toHaveTextContent(/Profile - Edit/);
  expect(alert).toHaveTextContent(/Profile updated successfully/);
});


test('can see error with backend issue for profile edit request', async () => {
  server.use(
    http.put('http://localhost:8000/api/v1/user/', () => {
      return HttpResponse.json(
        { message: 'Email already exists', },
        { status: 409, },
      );
    }),
  );
  const user = await initializeProfileEdit();

  const form = profileEditForm();
  await fillOutProfileEditForm(user, form);
  await user.click(form.updateButton);

  const pageTitles = screen.getAllByRole('heading', { level: 2 });
  const alert = screen.getByRole('alert');

  expect(pageTitles[0]).toHaveTextContent(/Profile - Edit/);
  expect(alert).toHaveTextContent(/Issue occurred during request: Email already exists/);
});


test('can see error with profile edit api call', async () => {
  server.use(
    http.put('http://localhost:8000/api/v1/user/', () => {
      return HttpResponse.error();
    }),
  );
  const user = await initializeProfileEdit();

  const form = profileEditForm();
  await fillOutProfileEditForm(user, form);
  await user.click(form.updateButton);

  const pageTitles = screen.getAllByRole('heading', { level: 2 });
  const alert = screen.getByRole('alert');

  expect(pageTitles[0]).toHaveTextContent(/Profile - Edit/);
  expect(alert).toHaveTextContent(/Error occurred during profile update./);
});


test('has change password', async () => {
  await initializeProfileEdit();

  const pageTitles = screen.getAllByRole('heading', { level: 2 });

  expect(pageTitles[1]).toHaveTextContent(/Change Password/);
});


test('change password has required form fields', async () => {
  await initializeProfileEdit();

  const form = changePasswordForm();

  expect(form.passwordField).toBeInvalid();
  expect(form.confirmPasswordField).toBeInvalid();
  expect(form.changePasswordButton).toBeDisabled();
});


test('can submit change password form', async () => {
  const user = await initializeProfileEdit();

  const form = changePasswordForm();
  await fillOutChangePasswordForm(user, form);

  expect(form.passwordField).toBeValid();
  expect(form.confirmPasswordField).toBeValid();
  expect(form.changePasswordButton).toBeEnabled();
});


test('taken to profile edit after successful password change', async () => {
  const user = await initializeProfileEdit();

  const form = changePasswordForm();
  await fillOutChangePasswordForm(user, form);
  await user.click(form.changePasswordButton);

  const pageTitles = screen.getAllByRole('heading', { level: 2 });
  const alert = screen.getByRole('alert');

  expect(pageTitles[0]).toHaveTextContent(/Profile - Edit/);
  expect(alert).toHaveTextContent(/Password has been changed/);
});


test('can see error with backend issue for change password request', async () => {
  server.use(
    http.put('http://localhost:8000/api/v1/user/', () => {
      return HttpResponse.json(
        {
          detail:[
            {
              loc: ['body','password'],
              msg: 'password needs to be at least 10 characters',
              type: 'value_error',
            }
          ]
        },
        { status: 422, },
      );
    }),
  );
  const user = await initializeProfileEdit();

  const form = changePasswordForm();
  await fillOutChangePasswordForm(user, form);
  await user.click(form.changePasswordButton);

  const pageTitles = screen.getAllByRole('heading', { level: 2 });
  const alert = screen.getByRole('alert');

  expect(pageTitles[0]).toHaveTextContent(/Profile - Edit/);
  expect(alert).toHaveTextContent(/password: password needs to be at least 10 characters/);
});


test('can see error with change password api call', async () => {
  server.use(
    http.put('http://localhost:8000/api/v1/user/', () => {
      return HttpResponse.error();
    }),
  );
  const user = await initializeProfileEdit();

  const form = changePasswordForm();
  await fillOutChangePasswordForm(user, form);
  await user.click(form.changePasswordButton);

  const pageTitles = screen.getAllByRole('heading', { level: 2 });
  const alert = screen.getByRole('alert');

  expect(pageTitles[0]).toHaveTextContent(/Profile - Edit/);
  expect(alert).toHaveTextContent(/Error occurred during password change./);
});
