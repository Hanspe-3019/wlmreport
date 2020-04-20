''' Class Servicedefintion
'''
from .export import export_to_excel
from .parsereport import parse_reportfile

class Servicedefinition:
    '''
   Parser eines ISPF-Print einer Service Definition

    A service definition consists of:

    - One or more service policies, which are named sets of overrides
        to the goals in the service definition. When a policy is activated,
        the overrides are merged with the service definition. You can have
        different policies to specify goals for different times.
        Service policies are activated by an operator command or through
        the ISPF administrative application utility.

    - Service classes, which are subdivided into periods, group work
        with similar performance goals, business importance, and resource
        requirements for management and reporting purposes. You assign
        performance goals to the periods within a service class.

    - Workloads, which aggregate a set of service classes for
        reporting purposes.

    - Report classes, which group work for reporting purposes.
        They are commonly used to provide more granular reporting for
        subsets of work within a single service class.

    - Resource groups, which define processor capacity boundaries
        within a system or across a sysplex. You can assign a minimum and
        maximum amount of CPU service units on general purpose processors,
        per second, to work by assigning a service class to a resource group.

    - Tenant resource groups and tenant report classes, which are
        comparable to resource groups and report classes. They allow for
        the metering and optional capping of workloads, along with the
        ability to map those workloads directly to Tailored Fit Pricing
        for IBM Z solutions.

    - Classification rules, which determine how to assign incoming
        work to a service class and report class or tenant report class.

    - Application environments, which are groups of application functions
        that execute in server address spaces and can be requested by a client.
        Workload management manages the work according to the defined goal,
        and automatically starts and stops server address spaces as needed.

    - Scheduling environments, which are lists of resource names along
        with their required states. If a z/OS® image satisfies all of the
        requirements in a scheduling environment, then units of work
        associated with that scheduling environment can be assigned
        to that z/OS image. Presently, JES2 and JES3 are the only participants
        that use scheduling environments.
    '''
    def __repr__(self):
        return 'Service Definition ' + self.service_definition

    def to_excel(self, path):
        ''' Export nach xlsx
        '''
        export_to_excel(self, path)

    def __init__(self, path):
        ''' path: Path zur Report File (ascii)
        '''
        self.service_definition = None
        self.workloads = {}
        self.resgroups = {}
        self.clfgroups = {}
        self.policies = {}
        self.ssmtypes = {}
        self.repclasses = {}
        self.applenvs = {}
        self.schedenvs = {}

        parse_reportfile(self, path)

        self.serviceclasses = {
            sc.name : sc
            for wl in self.workloads.values()
            for sc in wl.serviceclasses.values()
        }
