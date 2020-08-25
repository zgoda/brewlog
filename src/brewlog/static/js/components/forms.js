import { h } from 'preact';
import { useCallback, useEffect } from 'preact/hooks';

const Select = ((props) => {

  const handleChange = ((e) => {
    props.setValue(e.target.value);
  });

  return (
    <div class="field">
      <label class="label">{props.label}</label>
      <div class="select">
        <select value={props.value} onChange={handleChange}>
          {props.options.map((data) => (
            <option value={data.value}>{data.label}</option>
          ))}
        </select>
      </div>
    </div>
  )
});

const DateInput = ((props) => {

  const handleInput = ((e) => {
    props.setValue(e.target.value);
  });

  return (
    <div class="field">
      <label class="label" for={props.name}>{props.label}</label>
      <div class="control">
        <input class="input" type="date" name={props.name} onInput={handleInput} value={props.value} />
      </div>
    </div>
  )
});

const NumberInput = ((props) => {

  const handleInput = ((e) => {
    props.setValue(e.target.value);
  });

  return (
    <div class="field">
      <label class="label" for={props.name}>{props.label}</label>
      <div class="control">
        <input class="input" type="number" name={props.name} step={props.step} onInput={handleInput} value={props.value} />
      </div>
    </div>
  )
});

const TextArea = ((props) => {

  const handleInput = ((e) => {
    props.setValue(e.target.value);
  });

  return (
    <div class="field">
      <label class="label" for={props.name}>{props.label}</label>
      <div class="control">
        <textarea class="textarea" name={props.name} onInput={handleInput}>{props.value}</textarea>
      </div>
    </div>
  )
});

const CarbonationSelect = ((props) => {

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
    <Select value={props.carbonation} setValue={props.setCarbonation} label='Nagazowanie' options={options} />
  )
});

const CarbonationTypeSelect = ((props) => {

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
    <Select value={props.carbtype} setValue={props.setCarbType} label='Rodzaj nagazowania' options={options} />
  )
});

const SubmitButton = ((props) => {
  return (
    <div class="field">
      <div class="control">
        <button type="submit" class="button is-primary">{props.label}</button>
      </div>
    </div>
  )
});

const ModalForm = ((props) => {

  const onKeyDown = useCallback((e) => {
    if (e.keyCode === 27) {
      props.closeHandler();
    }
  }, [props]);

  useEffect(() => {
    window.addEventListener('keydown', onKeyDown);
    document.documentElement.classList.add('is-clipped');
    return () => {
      document.documentElement.classList.remove('is-clipped');
      window.removeEventListener('keydown', onKeyDown);
    }
  }, [onKeyDown]);


  let modalClass = 'modal';
  if (props.active) {
    modalClass = 'modal is-active';
  }

  return (
    <div class={modalClass}>
      <div class="modal-background" onClick={props.closeHandler} />
      <div class="modal-content">
        <div class="box">
          <p class="has-text-weight-bold">{props.label}</p>
          <form onSubmit={props.submitHandler}>
            {props.fields.map((field) => field)}
            <SubmitButton label='wyślij' />
          </form>
        </div>
      </div>
      <button class="modal-close is-large" aria-label="zamknij" onClick={props.closeHandler} />
    </div>
  )
});

const ActionButton = ((props) => {
  let classes = [
    'button', 'is-small', 'is-primary', 'is-light'
  ];
  if (props.theresMore) {
    classes.push('mr-2');
  }
  classes = classes.join(' ');

  return (
    <button class={classes} onClick={props.clickHandler}>{props.label}</button>
  )
});

const ActionLinkButton = ((props) => {
  return (
    <a class="button is-small is-primary is-light" href={props.url}>{props.label}</a>
  )
});

export { ActionButton, ActionLinkButton, CarbonationSelect, CarbonationTypeSelect, DateInput, ModalForm, NumberInput, SubmitButton, TextArea };
