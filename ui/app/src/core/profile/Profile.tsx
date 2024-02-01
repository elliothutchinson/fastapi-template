import { useEffect, useState } from 'react';
import { Form, INPUT, PASSWORD_INPUT, EMAIL_INPUT } from '../common/Components';
import { SUCCESS, ERROR } from '../header/Alert';
import { fetchProfile, updateProfile, changePassword } from './api';
  

const VIEW = 'view';
const EDIT = 'edit';


function ProfileView(props) {
  const fields = [
    {
      name: 'First Name',
      required: false,
      readOnly: true,
      type: INPUT,
      value: props.firstName,
    },
    {
      name: 'Last Name',
      required: false,
      readOnly: true,
      type: INPUT,
      value: props.lastName,
    },
    {
      name: 'Email',
      required: false,
      readOnly: true,
      type: INPUT,
      value: props.email,
    },
  ];

  const child = (
    <div key="edit" className="space-x-2">
      <a className="link" href="#profile" onClick={() => props.setProfileMode(EDIT)}>Edit</a>
    </div>
  );

  return (
    <Form formTitle="Profile - View" fields={fields} preChildren={[child]} requiredMessage=' ' />
  );
}


function EditProfileInfo(props) {
  const [firstName, setFirstName] = useState(props.firstName);
  const [lastName, setLastName] = useState(props.lastName);
  const [email, setEmail] = useState(props.email);

  const fields = [
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
  ];

  const child = (
    <div key="view" className="space-x-2">
      <a className="link" onClick={() => props.setProfileMode(VIEW)}>View</a>
    </div>
  );

  async function handleEditProfile() {
    const spinner = props.spinnerControl.create();
    const result = await updateProfile({
      firstName,
      lastName,
      email,
    }, props.authToken);
    props.spinnerControl.remove(spinner);
    console.log('update profile result: ', result);

    if (result.errors) {
      for (const error of result.errors) {
        props.alertControl.add({type: ERROR, message: error});
      }
    } else {
      props.alertControl.add({type: SUCCESS, message: 'Profile updated successfully'});
    }
  }

  const cta = {
    name: 'Update',
    handleClick: handleEditProfile,
  };

  return (
    <Form formTitle="Profile - Edit" fields={fields} preChildren={[child]} requiredMessage=' ' cta={cta} />
  );
}


function UpdatePassword(props) {
  const [password, setPassword] = useState('');
  const [passwordMatch, setPasswordMatch] = useState('');

  const fields = [
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

  async function handleChangePassword() {
    const spinner = props.spinnerControl.create();
    const result = await changePassword({
      password,
      passwordMatch,
    }, props.authToken);
    props.spinnerControl.remove(spinner);
    console.log('update password result: ', result);

    if (result.errors) {
      for (const error of result.errors) {
        props.alertControl.add({type: ERROR, message: error});
      }
    } else {
      props.alertControl.add({type: SUCCESS, message: 'Password has been changed'});
    }
  }

  const cta = {
    name: 'Change Password',
    handleClick: handleChangePassword,
  };

  return (
    <Form formTitle="Change Password" fields={fields} cta={cta} />
  );
}


function ProfileEdit(props) {

  return (
    <>
      <EditProfileInfo 
        alertControl={props.alertControl}
        spinnerControl={props.spinnerControl}
        setProfileMode={props.setProfileMode}
        firstName={props.firstName}
        lastName={props.lastName}
        email={props.email}
        authToken={props.authToken}
      />
      <div className="divider"></div>
      <UpdatePassword
        alertControl={props.alertControl}
        spinnerControl={props.spinnerControl}
        authToken={props.authToken}
      />
    </>
  );
}


export default function Profile(props) {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [profileMode, setProfileMode] = useState(VIEW);

  useEffect(() => {
    const fetchData = async () => {
      const spinner = props.spinnerControl.create();
      const result = await fetchProfile(props.authToken);
      props.spinnerControl.remove(spinner);
      console.log('fetch profile result: ', result);

      if (result.errors) {
        for (const error of result.errors) {
          props.alertControl.add({type: ERROR, message: error});
        }
      } else {
        setFirstName(result.data.firstName)
        setLastName(result.data.lastName)
        setEmail(result.data.email)
      }
    };
    fetchData();
  }, [profileMode]);

  let profileContent = null;

  if (profileMode === VIEW) {
    profileContent = <ProfileView
      setProfileMode={setProfileMode}
      firstName={firstName}
      lastName={lastName}
      email={email}
    />;
  } else if (profileMode === EDIT) {
    profileContent = <ProfileEdit
      alertControl={props.alertControl}
      spinnerControl={props.spinnerControl}
      setProfileMode={setProfileMode}
      firstName={firstName}
      lastName={lastName}
      email={email}
      authToken={props.authToken}
    />;
  }

  return (
    <>
      {profileContent}
    </>
  );
}
