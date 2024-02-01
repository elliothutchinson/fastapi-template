export const SUCCESS = 'success';
export const INFO = 'info';
export const WARNING = 'warning';
export const ERROR = 'error';


export default function AlertMessage(props) {
  const handleDismiss = () => {
    props.dismissAlert(props.alert);
  };

  // const alertClassName = `alert alert-success`;
  // const alertClassName = `alert alert-info`;
  // const alertClassName = `alert alert-warning`;
  // const alertClassName = `alert alert-error`;
  const alertClassName = `alert alert-${props.alert.type}`;

  return (
    <div className={alertClassName} role="alert">
      <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24" onClick={handleDismiss}>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span>{props.alert.message}</span>
    </div>
  );
}
