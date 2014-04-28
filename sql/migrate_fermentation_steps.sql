begin;
insert into fermentation_step(date, name, og, fg, volume, temperature, brew_id) values (
    select fermentation_start_date, 'primary', og, fg, brew_length, fermentation_temperature, id
    from brew
    where fermentation_start_date is not null
);
commit;
