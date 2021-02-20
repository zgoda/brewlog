import { h } from 'preact';
import { useCallback, useEffect } from 'preact/hooks';

const Select = (({ options, label, value, setValue }) => {

  const handleChange = ((e) => {
    setValue(e.target.value);
  });

  return (
    <div class="field">
      <label class="label">{label}</label>
      <div class="select">
        <select value={value} onChange={handleChange}>
          {options.map((data) => (
            <option value={data.value}>{data.label}</option>
          ))}
        </select>
      </div>
    </div>
  )
});

const DateInput = (({ name, label, value, setValue }) => {

  const handleInput = ((e) => {
    setValue(e.target.value);
  });

  return (
    <div class="field">
      <label class="label" for={name}>{label}</label>
      <div class="control">
        <input class="input" type="date" name={name} onInput={handleInput} value={value} />
      </div>
    </div>
  )
});

const NumberInput = (({ name, label, step, value, setValue }) => {

  const handleInput = ((e) => {
    setValue(e.target.value);
  });

  return (
    <div class="field">
      <label class="label" for={name}>{label}</label>
      <div class="control">
        <input class="input" type="number" name={name} step={step} onInput={handleInput} value={value} />
      </div>
    </div>
  )
});

const TextInput = (({ name, label, value, setValue }) => {

  const handleInput = ((e) => {
    setValue(e.target.value);
  });

  return (
    <div class="field">
      <label class="label" for={name}>{label}</label>
      <div class="control">
        <input class="input" type="text" name={name} onInput={handleInput} value={value} />
      </div>
    </div>
  )
});

const TextArea = (({ name, label, value, setValue }) => {

  const handleInput = ((e) => {
    setValue(e.target.value);
  });

  return (
    <div class="field">
      <label class="label" for={name}>{label}</label>
      <div class="control">
        <textarea class="textarea" name={name} onInput={handleInput}>{value}</textarea>
      </div>
    </div>
  )
});

const CarbonationSelect = (({ carbonation, setCarbonation }) => {

  const options = [
    {
      label: 'wysokie (np. niemiecka pszenica, belgijskie ale)',
      value: 'high'
    },
    {
      label: 'normalne (np. lager, amerykańskie ale)',
      value: 'normal'
    },
    {
      label: 'niskie (np. brytyjskie lub irlandzkie ale)',
      value: 'low'
    },
    {
      label: 'bardzo niskie (np kellerbier)',
      value: 'very low'
    },
    {
      label: 'żadne (np. sahti)',
      value: 'none'
    },
  ]

  return (
    <Select value={carbonation} setValue={setCarbonation} label='Nagazowanie' options={options} />
  )
});

const CarbonationTypeSelect = (({ carbType, setCarbType }) => {

  const options = [
    {
      label: 'wymuszone w kegu',
      value: 'forced in keg'
    },
    {
      label: 'refermentacja w kegu',
      value: 'keg with priming'
    },
    {
      label: 'refermentacja w butelkach',
      value: 'bottles with priming'
    }
  ]

  return (
    <Select value={carbType} setValue={setCarbType} label='Rodzaj nagazowania' options={options} />
  )
});

const SubmitButton = (({ label }) => {
  return (
    <div class="field">
      <div class="control">
        <button type="submit" class="button is-primary">{label}</button>
      </div>
    </div>
  )
});

const ModalForm = (({ label, fields, active, closeHandler, submitHandler }) => {

  const onKeyDown = useCallback((e) => {
    if (e.keyCode === 27) {
      closeHandler();
    }
  }, [closeHandler]);

  useEffect(() => {
    window.addEventListener('keydown', onKeyDown);
    document.documentElement.classList.add('is-clipped');
    return () => {
      document.documentElement.classList.remove('is-clipped');
      window.removeEventListener('keydown', onKeyDown);
    }
  }, [onKeyDown]);


  let modalClass = 'modal';
  if (active) {
    modalClass = 'modal is-active';
  }

  return (
    <div class={modalClass}>
      <div class="modal-background" onClick={closeHandler} />
      <div class="modal-content">
        <div class="box">
          <p class="has-text-weight-bold">{label}</p>
          <form onSubmit={submitHandler}>
            {fields.map((field) => field)}
            <SubmitButton label='wyślij' />
          </form>
        </div>
      </div>
      <button class="modal-close is-large" aria-label="zamknij" onClick={closeHandler} />
    </div>
  )
});

const ActionButton = (({ label, theresMore, clickHandler }) => {
  const classNames = [
    'button', 'is-small', 'is-primary', 'is-light'
  ];
  if (theresMore) {
    classNames.push('mr-2');
  }
  const classes = classNames.join(' ');

  return (
    <button class={classes} onClick={clickHandler}>{label}</button>
  )
});

const ActionLinkButton = (({ label, url, theresMore }) => {
  const classNames = [
    'button', 'is-small', 'is-primary', 'is-light'
  ];
  if (theresMore) {
    classNames.push('mr-2');
  }
  const classes = classNames.join(' ');

  return (
    <a class={classes} href={url}>{label}</a>
  )
});

export {
  h, ActionButton, ActionLinkButton, CarbonationSelect, CarbonationTypeSelect, DateInput,
  ModalForm, NumberInput, SubmitButton, TextArea, TextInput,
};
