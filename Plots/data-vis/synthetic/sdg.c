#include <stdio.h>
#include <math.h>
#include <sys/time.h>

#define FALSE 0
#define TRUE 1
#define NONE 0
#define UNIFORM 1
#define NORMAL 2
#define ABSOLUTE 0
#define HOURLY 1
#define DAILY 2
#define DAILYT 3
#define WEEKLY 4
#define MONTHLY 5
#define COMBINED 6
#define TRIGGER 7
#define PI 3.141592654

int debug = FALSE;


typedef struct device {
   char name[80];           /* Device name */
   int nstates;             /* Number of device states */
   char **states;           /* State descriptions */
   char current[80];        /* Current device state */
} *devptr;

typedef struct action {
   char *device;            /* Device affected by action */
   char *state;             /* State of device resulting from action */
   int order;               /* Time ordering time */
   int distribution;        /* Type of time probability distribution */
   int time;                /* Time at which action should fire */
   int v1;                  /* Value defining probability distribution */
   int v2;                  /* Value defining probability distribution */
} *aptr;

typedef struct scenario {
   char name[80];           /* Name of scenario */
   int initializer;         /* Type of scenario initializer */
   int ivalue;              /* Number of times scenario should fire */
   int *times;              /* Times to fire scenario */
   char **trigger;          /* Trigger value to fire scenario */
   int nactions;            /* Number of actions in scenario */
   struct action *actions;  /* Array of action structures in scenario */
} *sptr;


/*----------------------------------------------------------------------------
  ReadDevices reads device descriptions from the input file.
  ----------------------------------------------------------------------------*/

devptr ReadDevices(int numdevices, FILE *input)
{
   char str[80];
   int i, j, s;
   devptr devices;

   devices = (devptr) malloc(numdevices * sizeof(struct device)); 

   for (i=0; i<numdevices; i++) {             /* Read each device description */
      fscanf(input, "%s", devices[i].name);                    /* Device name */
                                                 /* Number of possible states */
      fscanf(input, "%d", &(devices[i].nstates));
      devices[i].states = (char **) malloc(devices[i].nstates * sizeof(char *));
      for (j=0; j<devices[i].nstates; j++) {            /* State descriptions */
	 if (j < (devices[i].nstates - 1))
            fscanf(input, "%s", str);
         else fscanf(input, "%s\n", str);
         devices[i].states[j] = (char *) malloc((strlen(str)+1) * sizeof(char));
         strcpy(devices[i].states[j], str);
      }
   }
   if (debug == TRUE)
      PrintDevices(numdevices, devices);
   return(devices);
}


/*----------------------------------------------------------------------------
  PrintDevices prints descriptions of the devices.
  ----------------------------------------------------------------------------*/

PrintDevices(int numdevices,                   /* Number of available devices */
             devptr devices)                    /* Array of device structures */
{
   int i, j;

   for (i=0; i<numdevices; i++) {
      printf("Device %s:  (", devices[i].name);
      for (j=0; j<devices[i].nstates-1; j++)
         printf("%s ", devices[i].states[j]);
      printf("%s)\n", devices[i].states[j]);
   }
}


/*----------------------------------------------------------------------------
  ReadAction reads a single action description from the input file.
  ----------------------------------------------------------------------------*/

void ReadAction(FILE *input,                                    /* Input file */
                aptr a)                                   /* Action structure */
{
   char str1[80], str2[80];

                       /* Read action effect as new state of specified device */
   fscanf(input, "%s %s", str1, str2);
   a->device = (char *) malloc((strlen(str1)+1) * sizeof(char));
   strcpy(a->device, str1);
   a->state = (char *) malloc((strlen(str2)+1) * sizeof(char));
   strcpy(a->state, str2);
   a->time = -1;

     /* Read action time relative to previous action or beginning of scenario */
   fscanf(input, "%s", str1);
   if (strcmp(str1, "NoOrder") == 0) {
      a->order = NONE;
   }
   else {
      if (strcmp(str1, "Uniform") == 0)
         a->order = UNIFORM;
      else if (strcmp(str1, "Normal") == 0)
         a->order = NORMAL;
      else {
         fprintf(stderr, "Time relation not recognized.\n");
	 exit(1);
      }
      fscanf(input, "%d %d\n", &(a->v1), &(a->v2));
   }
}


/*----------------------------------------------------------------------------
  PrintAction prints a description of an action.
  ----------------------------------------------------------------------------*/

void PrintAction(struct action a)                         /* Action structure */
{
   printf("  %s %s", a.device, a.state);
   if (a.order == NONE)
      printf(" NoOrder\n");
   else {
      if (a.order == UNIFORM)
         printf(" Uniform %d %d\n", a.v1, a.v2);
      else printf(" Normal %d %d\n", a.v1, a.v2);
   }
}


/*----------------------------------------------------------------------------
  PrintScenarios prints descriptions of the array of scenarios.
  ----------------------------------------------------------------------------*/

void PrintScenarios(int numscenarios,              /* The number of scenarios */
                    sptr scenarios)           /* Array of scenario structures */
{
   int i, j;
   struct scenario s;

   for (i=0; i<numscenarios; i++) {
      s = scenarios[i];
      printf("Scenario %s\n", s.name);
      if (scenarios[i].initializer == ABSOLUTE) {
         printf("Initialize at times\n");
         for (j=0; j<scenarios[i].ivalue; j++)
	    printf(" %d", scenarios[i].times[j]);
         printf("\n");
      }
      else if (scenarios[i].initializer == DAILYT) {
         printf("Initialize daily at times\n");
         for (j=0; j<scenarios[i].ivalue; j++)
	    printf(" %d", scenarios[i].times[j]);
         printf("\n");
      }
      else if (scenarios[i].initializer == HOURLY)
         printf("Initialize hourly %d times\n", scenarios[i].ivalue);
      else if (scenarios[i].initializer == DAILY)
         printf("Initialize daily %d times\n", scenarios[i].ivalue);
      else if (scenarios[i].initializer == WEEKLY)
         printf("Initialize weekly %d times\n", scenarios[i].ivalue);
      else if (scenarios[i].initializer == MONTHLY)
         printf("Initialize monthly %d times\n", scenarios[i].ivalue);
      else if (scenarios[i].initializer == COMBINED)
         printf("Initialize %d times total\n", scenarios[i].ivalue);
      else if (scenarios[i].initializer == TRIGGER)
         printf("Initialize based on trigger (%s %s)\n",
	          scenarios[i].trigger[0], scenarios[i].trigger[1]);
      for (j=0; j<s.nactions; j++) {
         PrintAction(s.actions[j]);
      }
   }
   printf("----------------------------------------------------------------\n");
   printf("                     Simulator Output\n");
   printf("----------------------------------------------------------------\n");
}


/*----------------------------------------------------------------------------
  ReadScenarios reads scenario descriptions from input file.
  ----------------------------------------------------------------------------*/

sptr ReadScenarios(int numscenarios,               /* The number of scenarios */
                   FILE *input)                                 /* Input file */
{
   char str[80], str1[80];
   int i, j;
   sptr scenarios;
                                       /* Create array of scenario structures */
   scenarios = (sptr) malloc(numscenarios * sizeof(struct scenario)); 

   for (i=0; i<numscenarios; i++) {                  /* Read in each scenario */
      fscanf(input, "%s\n", scenarios[i].name);         /* Read scenario name */
      fscanf(input, "%s", str);                   /* Read initialization type */
      if (strcmp(str, "trigger") == 0) {   /* Scenario files based on trigger */
         scenarios[i].initializer = TRIGGER;
	 fscanf(input, "%s %s\n", str, str1);     /* Trigger device and value */
	 scenarios[i].trigger = (char **) malloc(2 * sizeof(char *));
	 scenarios[i].trigger[0] =
	    (char *) malloc((strlen(str)+1) * sizeof(char));
	 scenarios[i].trigger[1] =
	    (char *) malloc((strlen(str1)+1) * sizeof(char));
         strcpy(scenarios[i].trigger[0], str);
         strcpy(scenarios[i].trigger[1], str1);
      }
      else {
         fscanf(input, "%d\n", &(scenarios[i].ivalue));
         scenarios[i].times = (int *) malloc(scenarios[i].ivalue * sizeof(int));
	                                  /* Scenario fires at absolute times */
	 if (strcmp(str, "absolute") == 0) {
	    scenarios[i].initializer = ABSOLUTE;
	    for (j=0; j<scenarios[i].ivalue; j++)
	       fscanf(input, "%d", &(scenarios[i].times[j]));
	 }
	 else if (strcmp(str, "dailyt") == 0) {  /* Fire daily at given times */
	    scenarios[i].initializer = DAILYT;
	    for (j=0; j<scenarios[i].ivalue; j++)
	       fscanf(input, "%d", &(scenarios[i].times[j]));
	 }
         else if (strcmp(str, "hourly") == 0)     /* Fire ivalue times hourly */
            scenarios[i].initializer = HOURLY;
         else if (strcmp(str, "daily") == 0)       /* Fire ivalue times daily */
            scenarios[i].initializer = DAILY;
         else if (strcmp(str, "weekly") == 0)     /* Fire ivalue times weekly */
            scenarios[i].initializer = WEEKLY;
         else if (strcmp(str, "monthly") == 0)   /* Fire ivalue times monthly */
            scenarios[i].initializer = MONTHLY;
	                           /* Fire ivalue times during simulated time */
         else if (strcmp(str, "combined") == 0)
            scenarios[i].initializer = COMBINED;
      }
      fscanf(input, "%d", &(scenarios[i].nactions));     /* Number of actions */
      scenarios[i].actions =
         (aptr) malloc(scenarios[i].nactions * sizeof(struct action));
      for (j=0; j<scenarios[i].nactions; j++) {    /* Read action information */
         ReadAction(input, &(scenarios[i].actions[j]));
      }
   }

   if (debug == TRUE)
      PrintScenarios(numscenarios, scenarios);  /* Print scenario information */
   return(scenarios);
}


/*----------------------------------------------------------------------------
  StringToDate converts string representing date and time to integer day and
  time values.
  ----------------------------------------------------------------------------*/

void StringToDate(char *str,             /* String representing date and time */
                  int *day,                               /* Day of the month */
		  int *time,                               /* Time of the day */
		  char date[11])                                      /* Date */
{
   int i;
   char dstr[3], hstr[3], mstr[3];

   for (i=0; i<11 && str[i]!='T'; i++)
      date[i] = str[i];
   date[i] = '\0';

   dstr[0] = str[8];
   dstr[1] = str[9];
   dstr[2] = '\0';
   hstr[0] = str[11];
   hstr[1] = str[12];
   hstr[2] = '\0';
   mstr[0] = str[14];
   mstr[1] = str[15];
   mstr[2] = '\0';

   *day = atoi(dstr) - 1;                     /* Days of the month start at 1 */
   *time = (atoi(hstr)*60) + atoi(mstr);
}


/*----------------------------------------------------------------------------
  DataToString converts integer day and time values to string representing
  date and time.
  ----------------------------------------------------------------------------*/

void DateToString(char date[11],             /* String representation of date */
                  int day,                                /* Day of the month */
		  int time,                                    /* Time of day */
		  char *str)         /* Date and time represented as a string */
{
   int i, cyear, cmonth, mdone, years, days, hours, minutes;
   char temp1[5], temp2[3], temp3[3], temp4[3];

   days = time / 1440;                          /* How many days have passed? */
   days += day;                                       /* Add in the start day */
   time = time % 1440;
   hours = time / 60;       /* How many hours have passed in the current day? */
   minutes = time % 60;    /* How many hours have passed in the current hour? */

                                                 /* Assume 365 days in a year */
   years = days / 365;                         /* How many years have passed? */
   strncpy(temp1, date, 4);
   temp1[4] = '\0';
   cyear = atoi(temp1);
   cyear += years;

   days = days % 365;
   temp1[0] = date[5];
   temp1[1] = date[6];
   temp1[2] = '\0';
   cmonth = atoi(temp1);

   mdone = FALSE;                       /* Find the current month of the year */
   for (i=0; i<=12 && mdone==FALSE; i++) {
      if ((cmonth == 1) || (cmonth == 3) || (cmonth == 5) || (cmonth == 7) ||
          (cmonth == 8) || (cmonth == 10) || (cmonth == 12)) {
	 days -= 31;
	 if (days >= 0)
	    if (cmonth < 12)
	       cmonth++;
	    else cmonth = 1;
	 else {
	    days += 31;
	    mdone = TRUE;
         }
      }
      else if (cmonth == 2) {
         days -= 28;
	 if (days >= 0)
	    cmonth++;
	 else {
	    days += 28;
	    mdone = TRUE;
         }
      }
      else if ((cmonth == 4) || (cmonth == 6) || (cmonth == 9) ||
               (cmonth == 11)) {
         days -= 30;
	 if (days >= 0)
	    cmonth++;
	 else {
	    days += 30;
	    mdone = TRUE;
         }
      }
   }

   if (cmonth < 10)
      sprintf(temp1, "0%d", cmonth);
   else sprintf(temp1, "%d", cmonth);
   if (days < 9)                              /* Days of the month start at 1 */
      sprintf(temp2, "0%d", days+1);
   else sprintf(temp2, "%d", days+1);
   if (hours < 10)
      sprintf(temp3, "0%d", hours);
   else sprintf(temp3, "%d", hours);
   if (minutes < 10)
      sprintf(temp4, "0%d", minutes);
   else sprintf(temp4, "%d", minutes);
   sprintf(str, "%d-%s-%sT%s:%s", cyear, temp1, temp2, temp3, temp4);
}


/*----------------------------------------------------------------------------
  Reseed determines the times at which a scenario should be fired next given
  the initialization value.
  ----------------------------------------------------------------------------*/

void Reseed(struct scenario s,                          /* Scenario structure */
            int time,                    /* Current simulated time in minutes */
	    int simtime)                   /* Total simulated time in minutes */
{
   int i, val;

                              /* Scenario should be fired ivalue times hourly */
   if (s.initializer == HOURLY)
      if ((time % 60) == 0) {
         for (i=0; i<s.ivalue; i++)
            s.times[i] = time + (rand() % 60);
   }
                               /* Scenario should be fired ivalue times daily */
   if (s.initializer == DAILY)
      if ((time % 1440) == 0) {
         for (i=0; i<s.ivalue; i++)
            s.times[i] = time + (rand() % 1440);
   }
                         /* Scenario should be fired daily at specified times */
   if (s.initializer == DAILYT)
      if ((time > 0) && ((time % 1440) == 0)) {
         for (i=0; i<s.ivalue; i++)
            s.times[i] += 1440;
   }
                              /* Scenario should be fired ivalue times weekly */
   if (s.initializer == WEEKLY)
      if ((time % 10080) == 0) {
         for (i=0; i<s.ivalue; i++)
            s.times[i] = time + (rand() % 10080);
   }
                             /* Scenario should be fired ivalue times monthly */
   if (s.initializer == MONTHLY)
      if ((time % 302400) == 0) {
         for (i=0; i<s.ivalue; i++)
            s.times[i] = time + (rand() % 302400);
   }
              /* Scenario should be fired ivalue times over simulation period */
   if (s.initializer == COMBINED)
      if (time == 0) {
         for (i=0; i<s.ivalue; i++)
            s.times[i] = time + (rand() % simtime);
   }
}


/*----------------------------------------------------------------------------
  GenerateNormalValue generates an integer value from a normal distribution
  with a specific mean and standard deviation.
  ----------------------------------------------------------------------------*/

int GenerateNormalValue(int mean,                               /* Mean value */
                        int stddev)                     /* Standard deviation */
{
   int i, start, end, r, done=FALSE, sum=0;
   float x, y, z;

   start = mean - (3 * stddev);
   end = mean + (3 * stddev);
   r = rand() % 10000;

   for (i=start; i<end; i++) {             /* The area under the curve is 1.0 */
      x = (float) (-1 * (i - mean) * (i - mean)) /
          (float) (2 * stddev * stddev);
      y = (float) exp((double) x);
      x = (float) stddev * (float) sqrt((double) 2.0 * PI);
      z = y / x;
      sum += (int) (z * 10000.0);
      if (sum >= r) {
         done = TRUE;
         return(i);
      }
   }

   return(end);
}


/*----------------------------------------------------------------------------
  FireScenario starts an instance of a scenario and determines when actions
  within the scenario should fire.
  ----------------------------------------------------------------------------*/

void FireScenario(struct scenario s,                    /* Scenario structure */
                  int time)              /* Current simulated time in minutes */
{
   int i, end = -1, val, order=FALSE, range, previous;
   aptr actions;

   if (debug == TRUE)
      printf("Firing scenario %s at time %d\n", s.name, time);
   actions = s.actions;
   previous = time; /* Action times are specified relative to previous action */

   for (i=0; i<s.nactions; i++) {          /* Determine times to fire actions */
      if (actions[i].order != NONE) {                /* The action is ordered */
         order = TRUE;
         if (actions[i].order == UNIFORM) {        /* Uniform time over range */
	    if (actions[i].v1 == actions[i].v2) /* Deterministic offset given */
	    {
	       actions[i].time = previous + actions[i].v1;
	       previous += actions[i].v1;
	    }
	    else {
	       val = rand();
	       val = (val % (actions[i].v2 - actions[i].v1)) + actions[i].v1;
	       actions[i].time = previous + val;
	       previous += val;
	    }
	 }
	 else if (actions[i].order == NORMAL) {   /* Normal time distribution */
	    val = GenerateNormalValue(actions[i].v1, actions[i].v2);
	    actions[i].time = previous + val;
	    previous = time + val;
	 }
                          /* Update range of action times for entire scenario */
	 if (actions[i].time > end)
	    end = actions[i].time;
      }
   }
                             /* Place unordered actions randomly within range */
   for (i=0; i<s.nactions; i++) {
             /* If all actions are unordered, time range is number of actions */
      if (order == TRUE)
         range = end - time;
      else range = s.nactions;

    /* Position the unordered actions randomly within the scenario time frame */
      if (actions[i].order == NONE) {
         val = rand();
	 val = (val % (range + 1)) + time;
	 actions[i].time = val;
      }
   }
}


/*----------------------------------------------------------------------------
  FindDevice finds a device corresponding to a given name.
  ----------------------------------------------------------------------------*/

struct device FindDevice(char *str,                            /* Device name */
                         int num,              /* Number of available devices */
			 devptr devices)        /* Array of device structures */
{
   int i;

   for (i=0; i<num; i++)
      if (strcmp(devices[i].name, str) == 0)
         return(devices[i]);
}

/*----------------------------------------------------------------------------
  CheckActions determines which actions are ready to execute and reports the
  action information.
  ----------------------------------------------------------------------------*/

void CheckActions(char *sname, /* Name of the scenario that fired this action */
                  int num,               /* Number of actions in the scenario */
		  aptr actions,                 /* Array of action structures */
                  int numdevices,              /* Number of available devices */
		  devptr devices,               /* Array of device structures */
		  int time,              /* Current simulated time in minutes */
		  char *date,                                   /* Start date */
		  int sday,                         /* Start day of the month */
		  int ptime)                           /* Current time of day */
{
   char str[80];
   int i;
   struct device d;

   for (i=0; i<num; i++)                   /* Determine which actions to fire */
      if (actions[i].time == time) {                           /* Fire action */
         d = FindDevice(actions[i].device, numdevices, devices);
	                  /* Only fire the action if it causes a state change */
	 if (strcmp(d.current, actions[i].state) != 0) {
	    strcpy(d.current, actions[i].state);
	    DateToString(date, sday, ptime, str);            /* Report action */
	    if (debug == TRUE)
	       printf("%s %s %s (scenario %s %d)\n",
	          str, d.name, d.current, sname, time);
	    else printf("%s %s %s\n", str, d.name, d.current);
         }
      }
}


/*----------------------------------------------------------------------------
  QueryScenario determines which if a scenario should be fired and if actions
  within a scenario are ready to be executed.
  ----------------------------------------------------------------------------*/

void QueryScenario(struct scenario s,                   /* Scenario structure */
                   int time,             /* Current simulated time in minutes */
		   int simtime,            /* Total simulated time in minutes */
		   int start,                        /* Start time in minutes */
		   int sday,                        /* Start day of the month */
		   char *date,                                  /* Start date */
                   int numdevices,             /* Number of available devices */
		   devptr devices)              /* Array of device structures */
{
   char str[80];
   int i;

   Reseed(s, time, simtime);     /* Determine when scenario needs to be fired */

                   /* Fire scenario if the current state contains the trigger */
   if (s.initializer == TRIGGER) {
      for (i=0; i<numdevices; i++)
         if (strcmp(devices[i].name, s.trigger[0]) == 0) {
	    if (strcmp(devices[i].current, s.trigger[1]) == 0)
	       FireScenario(s, time);
	    else return;
	 }
   }
   else {
      for (i=0; i<s.ivalue; i++)   /* Determine if scenario needs to be fired */
         if (s.times[i] == time)
            FireScenario(s, time);
   }
                                     /* Fire actions within scenario if ready */
   CheckActions(s.name, s.nactions, s.actions, numdevices, devices,
                time, date, sday, start+time);

   return;
}


/*----------------------------------------------------------------------------
  GenerateData is the clock-based simulator.  The initial time is determine
  and the initial state is set.  The clock is then incremented one minute at
  a time until then ending value is reached.  With each new clock value,
  each scenario is queried to see whether a new instance should be fired and
  if actions in the scenario are ready to be executed.
  ----------------------------------------------------------------------------*/

void GenerateData(FILE *input,                                  /* Input file */
                  int numdevices,              /* Number of available devices */
		  devptr devices,               /* Array of device structures */
                  int numscenarios,           /* Number of possible scenarios */
		  sptr scenarios)             /* Array of scenario structures */
{
   char str[80], date[11], hstr[3], mstr[3];
   int i, sday, start, time=0, simtime;
   struct device d;

                /* Read initial simulated time and date using ISO-8601 format */
   fscanf(input, "%s", str);
           /* Determine start time in minutes and start day from input string */
   StringToDate(str, &sday, &start, date);

   for (i=0; i<numdevices; i++) {               /* Generate the initial state */
      if (i < (numdevices-1))       /* Read in the initial state for a device */
         fscanf(input, "%s", str);
      else fscanf(input, "%s\n", str);
      d = devices[i];
      strcpy(d.current, str);
   }

   fscanf(input, "%d\n", &simtime);           /* Read in total simulated time */
   for (time=0; time<simtime; time++) {               /* Simulate each minute */
      for (i=0; i<numscenarios; i++)            /* Fire scenarios and actions */
         QueryScenario(scenarios[i], time, simtime, start, sday, date,
	               numdevices, devices);
   }

                                                /* Print finish time and date */
   DateToString(date, sday, start+simtime, str);
   if (debug == TRUE)
      printf("Finished %s\n", str);

   return;
}


/*----------------------------------------------------------------------------
  Main() seeds the random number generator, reads input information from the
  specified file, and starts the clock-based simulator.
  ----------------------------------------------------------------------------*/

main(int argc,
     char *argv[])
{
   FILE *input;
   int numdevices, numscenarios;
   devptr devices;
   sptr scenarios;
   struct timeval tv;
   struct timezone tz;

   if (argc > 1) {         /* Expected syntax is Executable InputFile [debug] */
      input = fopen(argv[1], "r");
      if (input == NULL) {
         fprintf(stderr, "File %s does not exist\n", argv[1]);
	 exit(1);
      }
      if (argc > 2) {
         printf("Debug on\n");
         debug = TRUE;
      }
   }
   else {
      fprintf(stderr, "Must supply input file name\n");
      exit(1);
   }

   gettimeofday(&tv, &tz);                /* Seed the random number generator */
   srand((int) tv.tv_usec);

   fscanf(input, "%d\n", &numdevices);         /* Read input file information */
   devices = ReadDevices(numdevices, input);
   fscanf(input, "%d\n", &numscenarios);
   scenarios = ReadScenarios(numscenarios, input);
                                                          /* Start simulation */
   GenerateData(input, numdevices, devices, numscenarios, scenarios);
   fclose(input);
}
