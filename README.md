# Download Manager

A download manager is a software tool that manages the downloading of files from the Internet.

## Usage 

Download the file for your operating system from [latest release](https://github.com/MarcoBenelli/download_manager/releases/latest). Alternatively, if you want to build the application on your own, follow the instructions in the [Build](#build) section.

## Requirements

These are the requirements in case you want to build the application, they are not needed in case you just want to run the release.

program |required
--------|--------
`python`|yes
`make`  |no
`git`   |no

## Build

Clone the repository in a directory of your choice:
```sh
git clone https://github.com/MarcoBenelli/download_manager
```

Open `download_manager` project folder:
```sh
cd download_manager
```

Create and activate a virtual environment (this step is optional and can be done in many different ways, e. g. you might want to use `conda`).
On Unix-like systems, you could do it like this:
```sh
python3 -m venv env
. env/bin/activate
```
On Windows PowerShell, you could do it like this:
```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

Install the dependencies:
```sh
make install
```

Build the application, the output will be in `dist`:
```sh
make
```

## Features

These are some of the features my GUI implements:
* A working Download Manager: my GUI implements the basic functionality of a Download Manager - it allows the user to specify a URL in the entry at the top, starts the download when the user presses the `Return` key and adds it to the list of active downloads below, and notifies the user of progress with a progressbar until it finishes.
* Configuration options: my implementation supplies the user with an interface to specify the download directory (*Edit* > *Change download directory*).
* Pause, restart, and cancel: my Download Manager allows the user to pause a download, cancel a download, or restart a paused download at a later time (within the same session) by right-clicking on the progressbar.

My Download Manager implementation also support the following features:
* History: my GUI maintains a persistent history of downloads.
There is a view that lists all completed/aborted downloads the user has executed, with statistics on time started and time completed (*View* > *History*).
* Resume download: in addition to saving a persistent history, if the user closes the application my GUI saves the state of all downloads in progress.
When the GUI is launched again, it resumes the downloads in progress.

## License

Licensed under the term of [GNU GPL v3.0](LICENSE).
