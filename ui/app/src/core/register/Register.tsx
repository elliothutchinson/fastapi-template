import { useState } from 'react';
import { LOGIN_PAGE } from '../common/contants';
import { Form, INPUT, PASSWORD_INPUT, EMAIL_INPUT } from '../common/Components';
import { registerUser } from './api';
import { SUCCESS, ERROR } from '../header/Alert';


export default function Register(props) {
  const [username, setUsername] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [passwordMatch, setPasswordMatch] = useState('');

  const fields = [
    {
      name: 'Username',
      required: true,
      type: INPUT,
      value: username,
      handleChange: setUsername,
    },
    {
      name: 'First Name',
      required: true,
      type: INPUT,
      value: firstName,
      handleChange: setFirstName,
    },
    {
      name: 'Last Name',
      required: true,
      type: INPUT,
      value: lastName,
      handleChange: setLastName,
    },
    {
      name: 'Email',
      required: true,
      type: INPUT,
      inputType: EMAIL_INPUT,
      value: email,
      handleChange: setEmail,
    },
    {
      name: 'Password',
      required: true,
      type: INPUT,
      inputType: PASSWORD_INPUT,
      value: password,
      handleChange: setPassword,
    },
    {
      name: 'Confirm Password',
      required: true,
      type: INPUT,
      inputType: PASSWORD_INPUT,
      value: passwordMatch,
      handleChange: setPasswordMatch,
    },
  ];

  const child = (
    <div key="register" className="space-x-2">
      <span>Already have an account?</span>
      <a className="link" href="#login" onClick={() => props.setActivePage(LOGIN_PAGE)}>Login</a>
    </div>
  );

  async function handleRegister(e) {
    e.preventDefault();
    const spinner = props.spinnerControl.create();
    const result = await registerUser({
      username,
      firstName,
      lastName,
      email,
      password,
      passwordMatch,
    });
    props.spinnerControl.remove(spinner);
    console.log('register result: ', result);

    if (result.errors) {
      for (const error of result.errors) {
        props.alertControl.add({type: ERROR, message: error});
      }
    } else {
      props.alertControl.add({type: SUCCESS, message: 'User registered successfully'});
      props.setActivePage(LOGIN_PAGE);
    }
  }

  const cta = {
    name: 'Register',
    handleClick: handleRegister,
  };

  return (
    <Form formTitle="Register" fields={fields} children={[child]} cta={cta} />
  );
}
