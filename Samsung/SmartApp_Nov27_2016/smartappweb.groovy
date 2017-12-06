/**
 *  SmartAppWeb
 *
 *  Copyright 2016 Vasudevan Nagendra
 *
 *  Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
 *  in compliance with the License. You may obtain a copy of the License at:
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
 *  on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License
 *  for the specific language governing permissions and limitations under the License.
 *
 */
mappings {
  path("/switches") {
    action: [
      GET: "listSwitches"
    ]
  }
  path("/switches/:command") {
    action: [
      PUT: "updateSwitches"
    ]
  }
  path("/contacts") {
    action: [
      GET: "listContacts"
    ]
  }
  path("/motionsensors") {
    action: [
      GET: "listMotionSensors"
    ]
  }
}

definition(
    name: "SmartAppWeb",
    namespace: "SmartAppforWeb",
    author: "Vasudevan Nagendra",
    description: "Smart App for accessing through the Web",
    category: "SmartThings Labs",
    iconUrl: "https://s3.amazonaws.com/smartapp-icons/Convenience/Cat-Convenience.png",
    iconX2Url: "https://s3.amazonaws.com/smartapp-icons/Convenience/Cat-Convenience@2x.png",
    iconX3Url: "https://s3.amazonaws.com/smartapp-icons/Convenience/Cat-Convenience@2x.png",
    oauth: true)


preferences {
  section ("Allow external service to control these things...") {
    input "switches", "capability.switch", multiple: true, required: true
    //input "switch2", "capability.switch", multiple: false, required: true
    input "contacts", "capability.contactSensor", multiple: true, required: true
    input "motionsensors", "capability.motionSensor", multiple: true, required: true
  }
}

def installed() {
	log.debug "Installed with settings: ${settings}"
    initialize()
}

def updated() {
	log.debug "Updated with settings: ${settings}"
	unsubscribe()
	initialize()
}

def initialize() {
	// TODO: subscribe to attributes, devices, locations, etc.
    subscribe(contacts, "contacts", contactHandler)
    subscribe(motionsensors, "motionsensors", motionHandler)
}

def contactHandler(evt) {
  if("open" == evt.value)
    // contact was opened, turn on a light maybe?
    log.debug "Contact is in ${evt.value} state"
  if("closed" == evt.value)
    // contact was closed, turn off the light?
    log.debug "Contact is in ${evt.value} state"
}

def motionHandler(evt) {
    if (evt.value == "active") {
        // motion detected
    } else if (evt.value == "inactive") {
        // motion stopped
    }
}

def listSwitches() {
    def resp = []
    switches.each {
      resp << [name: it.displayName, value: it.currentValue("switch")]
    }
    return resp
}

def listContacts() {
    def resp = []
    contacts.each {
      resp << [name: it.displayName, value: it.currentValue("contact")]
    }
    return resp
}

def listMotionSensors() {
    def resp = []
    motionsensors.each {
      resp << [name: it.displayName, value: it.currentValue("motion")]
    }
    return resp
}

def updateSwitches() {
    // use the built-in request object to get the command parameter
    def command = params.command

    // all switches have the command
    // execute the command on all switches
    // (note we can do this on the array - the command will be invoked on every element
    switch(command) {
        case "on":
            switches.on()
            break
        case "off":
            switches.off()
            break
        default:
            httpError(400, "$command is not a valid command for all switches specified")
    }
}

// TODO: implement event handlers
