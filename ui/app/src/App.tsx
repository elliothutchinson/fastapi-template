import { useState } from 'react';
import './App.css';
import { stateListControlFactory } from './core/common/utils';
import { LOGIN_PAGE, REGISTER_PAGE, PROFILE_PAGE, TODO_PAGE } from './core/common/contants';
import Header from './core/header/Header';
import Login from './core/login/Login';
import Register from './core/register/Register';
import Profile from './core/profile/Profile';
import Todo from './core/todo/Todo';
import Footer from './core/footer/Footer';


export default function App() {
  const [alerts, setAlerts] = useState([]);
  const [activePage, setActivePage] = useState(LOGIN_PAGE);
  const [user, setUser] = useState({});
  const [authToken, setAuthToken] = useState({});
  const [loading, setLoading] = useState([]);

  const alertControl = stateListControlFactory(setAlerts);
  const spinnerControl = stateListControlFactory(setLoading);

  function isLoading() {
    return loading.length > 0;
  }

  function setActivePageWrapper(nextActivePage) {
    location.hash = nextActivePage;
    setActivePage(nextActivePage);
  }

  let page = null;
  
  if (activePage === LOGIN_PAGE) {
    location.hash = LOGIN_PAGE;
    page = <Login
      alertControl={alertControl}
      spinnerControl={spinnerControl}
      setActivePage={setActivePageWrapper}
      setUser={setUser}
      setAuthToken={setAuthToken}
    />;
  } else if (activePage === REGISTER_PAGE) {
    page = <Register 
      alertControl={alertControl}
      spinnerControl={spinnerControl}
      setActivePage={setActivePageWrapper}
    />;
  } else if (activePage === PROFILE_PAGE) {
    page = <Profile
      alertControl={alertControl}
      spinnerControl={spinnerControl}
      authToken={authToken}
    />;
  } else if (activePage === TODO_PAGE) {
    page = <Todo
      alertControl={alertControl}
      spinnerControl={spinnerControl}
      authToken={authToken}
    />;
  }

  return (
    <>
      <div className='container mx-auto'>
        <Header
          alerts={alerts}
          alertControl={alertControl}
          spinnerControl={spinnerControl}
          activePage={activePage}
          setActivePage={setActivePageWrapper}
          authToken={authToken}
          setAuthToken={setAuthToken}
          user={user}
          setUser={setUser}
          loading={isLoading()}
        />
        {page}
      </div>
      <Footer />
    </>
  );
}
