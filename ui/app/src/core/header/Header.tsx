import { LOGIN_PAGE, REGISTER_PAGE, PROFILE_PAGE, TODO_PAGE, APP_NAME } from '../common/contants';
import AlertMessage from './Alert';
import { logoutUser } from './api';


function Nav(props) {
  const todoOnClick = () => props.setActivePage(TODO_PAGE);
  const profileOnClick = () => props.setActivePage(PROFILE_PAGE);

  async function handleLogout() {
    const spinner = props.spinnerControl.create();
    const result = await logoutUser(props.authToken);
    props.spinnerControl.remove(spinner);
    console.log('logout result: ', result);

    if (result.errors) {
      for (const error of result.errors) {
        props.alertControl.add({type: ERROR, message: error});
      }
    } else {
      props.setUser({});
      props.setAuthToken({});
      props.setActivePage(LOGIN_PAGE);
    }
  }

  return (
    <div className="navbar bg-base-100">
      <div className="navbar-start">
        <div className="dropdown">
          <label tabIndex={0} className="btn btn-ghost md:hidden">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h8m-8 6h16" />
            </svg>
          </label>
          <ul tabIndex={0} className="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
            <li><a onClick={todoOnClick}>Todos</a></li>
            <li><a onClick={profileOnClick} href="#profile">{props.user.username}</a></li>
          </ul>
        </div>
        <a className="btn btn-ghost normal-case text-xl" onClick={todoOnClick}>{APP_NAME}</a>
      </div>
      <div className="navbar-center hidden md:flex">
        <ul className="menu menu-horizontal px-1">
          <li><a onClick={todoOnClick}>Todos</a></li>
          <li><a onClick={profileOnClick}>{props.user.username}</a></li>
        </ul>
      </div>
      <div className="navbar-end">
        <a className="btn" onClick={handleLogout}>Logout</a>
      </div>
    </div>
  );
}


export default function Header(props) {
  const invisibleSpinner = <span className="opacity-0 loading loading-ring loading-xs"></span>;
  const spinner = props.loading ? <span className="opacity-100 loading loading-ring loading-xs"></span> : invisibleSpinner;
  const hideNav = props.activePage === LOGIN_PAGE || props.activePage === REGISTER_PAGE;
  const nav = hideNav ? null :
    <Nav
      setActivePage={props.setActivePage}
      user={props.user}
      setUser={props.setUser}
      alertControl={props.alertControl}
      spinnerControl={props.spinnerControl}
      authToken={props.authToken}
      setAuthToken={props.setAuthToken}
    />;
  const alerts = props.alerts
    .map(a => <AlertMessage key={a.id} dismissAlert={props.alertControl.remove} alert={a} />);

  return (
    <>
      <div className="hero bg-base-200">
        <div className="hero-content text-center">
          <div className="max-w-md">
              <div className="flex justify-center">
                {invisibleSpinner}
                <h1 className="text-5xl font-bold">{APP_NAME}</h1>
                {spinner}
              </div>
          </div>
        </div>
      </div>
      {nav}
      {alerts}
    </>
  );
}
