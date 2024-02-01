export const INPUT = 'input';
export const SELECT = 'select';
export const CHECKBOX = 'checkbox';
export const TEXT_INPUT = 'text';
export const PASSWORD_INPUT = 'password';
export const EMAIL_INPUT = 'email';


export function Modal(props) {
  const modalCancel = <button className="btn" onClick={props.toggleModal}>Cancel</button>;

  return (
    <>
      <dialog id={props.modalId} className="modal modal-bottom sm:modal-middle">
      <div className="modal-box">
        {props.modalState ? props.children : null}
        <div className="modal-action">
          <form method="dialog">
            {/* if there is a button in form, it will close the modal */}
            {props.modalState ? modalCancel : null}
          </form>
        </div>
      </div>
      </dialog>
    </>
  );
}
  

export function InputField(props) {
  const fieldName = props.required ? `${props.name} *` : props.name;

  return (
      <div className="form-control w-full max-w-xs">
        <label className="label" htmlFor={props.name}>
          <span className="label-text">{fieldName}</span>
        </label>
        <input
          className="input input-bordered w-full max-w-xs"
          id={props.name}
          type={props.type} 
          placeholder={props.name}
          required={props.required}
          disabled={props.disabled}
          readOnly={props.readOnly}
          value={props.value}
          onChange={(e) => props.handleChange(e.target.value)}
        />
      </div>
  );
}


export function SelectField(props) {
  const fieldName = props.required ? `${props.name} *` : props.name;
  const options = props.options.map(o => <option key={o.value} value={o.value}>{o.name}</option>);

  return (
    <div className="form-control w-full max-w-xs">
      <label className="label" htmlFor={props.name}>
        <span className="label-text">{fieldName}</span>
      </label>
      <select 
        className="select w-full max-w-xs"
        id={props.name}
        required={props.required}
        disabled={props.disabled}
        readOnly={props.readOnly}
        value={props.value}
        onChange={(e) => props.handleChange(e.target.value)}
      >
        {options}
      </select>
    </div>
  );
}


export function CheckboxField(props) {
  const fieldName = props.required ? `${props.name} *` : props.name;

  return (
    <div className="form-control">
      <label className="label cursor-pointer" htmlFor={props.name}>
        <span className="label-text">{fieldName}</span> 
        <input
          className="checkbox"
          id={props.name}
          disabled={props.disabled}
          readOnly={props.readOnly}
          type="checkbox"
          checked={props.value}
          onChange={() => props.handleChange(!props.value)}
        />
      </label>
    </div>
  );
}


export function Form(props) {
  const fields = props.fields.map(f => {
    let formField = null;
    if (f.type === INPUT) {
      const inputType = f.inputType || TEXT_INPUT;
      formField = <InputField
        key={f.name}
        required={f.required}
        disabled={f.disabled}
        readOnly={f.readOnly}
        type={inputType}
        name={f.name}
        value={f.value}
        handleChange={f.handleChange}
      />;
    } else if (f.type === SELECT) {
      formField = <SelectField
        key={f.name}
        required={f.required}
        disabled={f.disabled}
        readOnly={f.readOnly}
        name={f.name}
        options={f.options}
        value={f.value}
        handleChange={f.handleChange}
      />;
    } else if (f.type === CHECKBOX) {
      formField = <CheckboxField
        key={f.name}
        required={f.required}
        disabled={f.disabled}
        readOnly={f.readOnly}
        name={f.name}
        value={f.value}
        handleChange={f.handleChange}
      />
    }
    return formField;
  });

  function isValid() {
    const invalidFields = props.fields.filter(f => !f.readOnly && f.required && !f.value);

    return invalidFields.length > 0;
  }

  const requiredMessage = props.requiredMessage || "* Required";
  const validForm = isValid();
  const ctaButton = !props.cta ? null :
    <button className="btn btn-primary" type="submit" disabled={validForm}>{props.cta.name}</button>;
  const ctaAction = !props.cta ? null : props.cta.handleClick;

  return (
    <>
      <h2 className="text-2xl text-center">{props.formTitle}</h2>
        <form onSubmit={ctaAction}>
          <div className="grid place-content-center space-y-4">
            {props.preChildren}
            {fields}
            <div className="text-xs">{requiredMessage}</div>
            {ctaButton}
            {props.children}
          </div>
        </form>
    </>
  );
}
