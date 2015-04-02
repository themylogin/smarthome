float cadence = 0;
float speed = 0;

void setup()
{
  pinMode(2, INPUT_PULLUP);
  pinMode(3, INPUT_PULLUP);
  
  // TIMER SETUP- the timer interrupt allows precise timed measurements of the reed switch
  //for more info about configuration of arduino timers see http://arduino.cc/playground/Code/Timer1
  cli();//stop interrupts

  //set timer1 interrupt at 1kHz
  TCCR1A = 0;// set entire TCCR1A register to 0
  TCCR1B = 0;// same for TCCR1B
  TCNT1  = 0;
  // set timer count for 1khz increments
  OCR1A = 1999;// = (1/1000) / ((1/(16*10^6))*8) - 1
  // turn on CTC mode
  TCCR1B |= (1 << WGM12);
  // Set CS11 bit for 8 prescaler
  TCCR1B |= (1 << CS11);   
  // enable timer compare interrupt
  TIMSK1 |= (1 << OCIE1A);
  
  sei();//allow interrupts
  //END TIMER SETUP
  
  Serial.begin(9600);
}

int v;
int value2, state2 = -1, counter2 = 0, timer2 = 0;
int value3, state3 = -1, counter3 = 0, timer3 = 0;
ISR(TIMER1_COMPA_vect)
{
  v = digitalRead(2);
  if (value2 != v)
  {
    counter2 = 25;
    value2 = v;
  }
  if (counter2 > 0)
  {
    counter2--;
  }
  else
  {
    if (state2 != value2)
    {
      state2 = value2;
      if (state2 == 0)
      {
        speed = 2401.0 * 3.6   / timer2;
        timer2 = 0;
      }
    }
  }
  if (timer2 > 2000)
  {
    speed = 0;
  }
  else
  {
    timer2++;
  } 
  
  
  v = digitalRead(3);
  if (value3 != v)
  {
    counter3 = 25;
    value3 = v;
  }
  if (counter3 > 0)
  {
    counter3--;
  }
  else
  {
    if (state3 != value3)
    {
      state3 = value3;
      if (state3 == 0)
      {
        cadence = 60000.0 / timer3;
        timer3 = 0;
      }
    }
  }
  if (timer3 > 2000)
  {
    cadence = 0;
  }
  else
  {
    timer3++;
  } 
}

void loop()
{
  analogWrite(5, 160 * speed / 60.0);
  analogWrite(6, 160 * cadence / 120.0);
}

