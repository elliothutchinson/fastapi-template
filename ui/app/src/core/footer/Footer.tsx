import { APP_NAME, APP_VERSION } from '../common/contants';


export default function Footer(props) {

  return (
    <footer className="footer footer-center p-4 bg-base-300 text-base-content">
      <aside>
        <p>{APP_NAME} - {APP_VERSION}</p>
      </aside>
    </footer>
  );
}
