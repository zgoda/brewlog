import { h } from 'preact';

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
})

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

export { CarbonationSelect, CarbonationTypeSelect, DateInput, NumberInput, TextArea };
