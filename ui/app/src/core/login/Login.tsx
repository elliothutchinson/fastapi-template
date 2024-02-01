import { useState } from 'react';
import { REGISTER_PAGE, TODO_PAGE } from '../common/contants';
import { Form, INPUT, PASSWORD_INPUT } from '../common/Components';
import { loginUser } from './api';
import { ERROR } from '../header/Alert';


export default function Login(props) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const fields = [
    {
      name: 'Username',
      required: true,
      type: INPUT,
      value: username,
      handleChange: setUsername,
    },
    {
      name: 'Password',
      required: true,
      type: INPUT,
      inputType: PASSWORD_INPUT,
      value: password,
      handleChange: setPassword,
    },
  ];

  async function handleLogin(e) {
    e.preventDefault();
    const spinner = props.spinnerControl.create();
    const result = await loginUser({
      username,
      password,
    });
    props.spinnerControl.remove(spinner);
    console.log('login result: ', result);

    if (result.errors) {
      for (const error of result.errors) {
        props.alertControl.add({type: ERROR, message: error});
      }
    } else {
      props.setUser({username});
      props.setAuthToken(result.data);
      props.setActivePage(TODO_PAGE);
    }
  }

  const child = (
    <div key="login" className="space-x-2">
      <span>Don't have an account?</span>
      <a className="link" href="#register" onClick={() => props.setActivePage(REGISTER_PAGE)}>Register</a>
    </div>
  );

  const cta = {
    name: 'Login',
    handleClick: handleLogin,
  };

  return (
    <Form formTitle="Login" fields={fields} children={[child]} cta={cta} />
  );
}
