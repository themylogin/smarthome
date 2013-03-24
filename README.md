Architecture
============

Smart home consists of multiple objects (as ```object``` is a reserved python keyword, we call them **smart**s) interacting with each other. Interaction is accomplished via **signal**/slot mechanism. Smarts have **state**s — read-only variables that represent real world conditions and can perform **action**s that can lead to changes in them.

Smart is a class wrapper with ```architecture.smart``` decorator. As it get it's instance name from deep code introspection (even bytecode introspection; that's why we require CPython), it must be assigned to a variable (e.g. ```front_door = Door()```). Smart classes can be divided in following groups (each class declaration should be but to corresponding package):
 * **Interface** deals with low-level technical objects such as I/O ports, files and network connections; they are smart home's eyes and ears. Most of the signals are initiated after reading from interfaces and most of the actions are performed by writing into them. 
 * **Object** is a real-world object such as door or lamp, usually connected to some interface. Object classes translate from computer interface language (e.g. specific bit was set to zero) to human language (e.g. door was closed) and vice versa.
 * **Watcher** observes multiple objects (e.g. door and key holder) and makes conclusions (e.g. owner has just left).
 * **Servant** gets information from observers and performs different actions to make home smart (e.g. when owner comes into apartment late night, servant turns on the light).
 * **Tool**s stands of this hierarchy; they just help watchers and servants in their heavy work.

Signals are ```architecture.signal``` class instances. For the same reason (their names are retrieved from code introspection), they must be constructed only in smart ```__init__``` and stored to instance variable either via explicit assigment (e.g. ```self.open = signal()```) or via ```setattr``` (e.g. ```setattr(self, "bit%dOn" % (bit,), signal())```). Signal are emited just by calling: ```self.open()```. These calls can contain any arguments (e.g. ```self.stateChanged(newState=self.state)```). When smart wants to subscribe to a signal, it **connect**s it to own handler via ```architecture.connect```: ```connect(door.opened, lambda: light.turnOn())```. Handler must accept all arguments that are passed when emiting a signal.

States and actions can be exposed via corresponding ```architecture.state``` and ```architecture.action``` functions that can act either as decorators when declaring smart class method or as wrappers for callables (e.g. ```self.turnOn = action(lambda: iface.out(1))```). Assignment rules are the same as ones for signals. Actions can accept arguments and states obviously can't.
