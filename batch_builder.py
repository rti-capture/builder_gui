#!/usr/bin/python

import os
import subprocess
import sys
import time

if sys.platform == 'darwin':
     sys.path.append('/usr/local/lib/python2.7/site-packages')

import pygtk
pygtk.require('2.0')
import gtk

lp_file = "/usr/local/share/generic.lp"
fitter_script = "/usr/local/bin/fitter-script"

# map of return code -> error messages from filter_script 
MESSAGES =  {0: "Fitting completed",
           1: "Error: Wrong parameters sent",
           2: "Error: Not a valid PTM hierachy",
           3: "Error: LP file not found",
           4: "Error: No Valid NEF/JPEG files found"}

class RTIFitterGUI:

    # directory chooser code from John's code
    def folderchoose_cb(self, widget, data = None):
        chooser = gtk.FileChooserDialog('Select folder to be processed', self.window,
                gtk.FILE_CHOOSER_ACTION_CREATE_FOLDER,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, 'Select', 99))
        chooser.set_default_response(99)
        chooser.set_current_folder("~")
        response = chooser.run()
        filename = chooser.get_filename()
        chooser.hide()
        print filename
        if filename is None:
            print "No folder selected doing nothing"
        else:
            self.button1.hide
            # filter out non-directories
            paths_to_process = [os.path.join(filename, p) for p in os.listdir(filename) if os.path.isdir(os.path.join(filename, p))]
            if not paths_to_process:
                self.show_message("Error: No paths to process in the selected folder")
                return
            errors = {}  # a map of processed paths to errors
            for path in paths_to_process:
                retVal = self.do_process(path)
                if retVal:
                    errors[path] = MESSAGES.get(retVal, "Error: Something really unexpected went wrong")
            if errors:
                # display error messages from all failures
                self.show_message("\n".join(["%s: %s" % (p, m) for (p, m) in errors.items()]))
            else:
                # success
                self.show_message(MESSAGES[0], message_type=gtk.MESSAGE_INFO)
             self.button1.show

    # process a single path
    def do_process(self, path):
        fitps = subprocess.Popen(args ="%s \"%s\" \"%s\""% (fitter_script, lp_file, path),
                    shell = True,
                    stdout = sys.stdout,
                    stderr = sys.stderr)
        return fitps.wait()

    # display a message dialog to the user
    def show_message(self, message, message_type=gtk.MESSAGE_ERROR):
        md = gtk.MessageDialog(self.window,
                gtk.DIALOG_DESTROY_WITH_PARENT, message_type,
                gtk.BUTTONS_CLOSE, message)
        md.run()
        md.destroy()

    # another callback
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False

    def __init__(self):
        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        self.window.set_title("PTM fitter helper")

        # Here we just set a handler for delete_event that immediately
        # exits GTK.
        self.window.connect("delete_event", self.delete_event)

        # Sets the border width of the window.
        self.window.set_border_width(10)

        # We create a box to pack widgets into.
        self.box1 = gtk.HBox(False, 0)

        # Put the box into the main window.
        self.window.add(self.box1)

        # Creates a new button with the label
        self.button1 = gtk.Button("Build")

        # Now when the button is clicked, we call the "callback" method
        # with a pointer to "button 1" as its argument
        self.button1.connect("clicked", self.folderchoose_cb, "Choose Folder")

        # Instead of add(), we pack this button into the invisible
        # box, which has been packed into the window.
        self.box1.pack_start(self.button1, True, True, 0)
        # this button is complete, and it can now be displayed.
        self.button1.show()

        # Do these same steps again to create a second button
        self.button2 = gtk.Button("Quit")

        self.button2.connect("clicked", self.delete_event, "Quit")
        self.box1.pack_start(self.button2, True, True, 0)

        self.button2.show()
        self.box1.show()
        self.window.show()


def main():
    gtk.main()

if __name__ == "__main__":
    fitter = RTIFitterGUI()
    main()