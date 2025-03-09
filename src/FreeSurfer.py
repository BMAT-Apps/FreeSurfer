#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 14:25:40 2021

@author: ColinVDB
Template
"""


import sys
import os
from os.path import join as pjoin
from os.path import exists as pexists
# from dicom2bids import *
import logging
from PyQt5.QtCore import (QSize,
                          Qt,
                          QModelIndex,
                          QMutex,
                          QObject,
                          QThread,
                          pyqtSignal,
                          QRunnable,
                          QThreadPool, 
                          QEvent)
from PyQt5.QtWidgets import (QDesktopWidget,
                             QApplication,
                             QWidget,
                             QPushButton,
                             QMainWindow,
                             QLabel,
                             QLineEdit,
                             QVBoxLayout,
                             QHBoxLayout,
                             QFileDialog,
                             QDialog,
                             QTreeView,
                             QFileSystemModel,
                             QGridLayout,
                             QPlainTextEdit,
                             QMessageBox,
                             QListWidget,
                             QTableWidget,
                             QTableWidgetItem,
                             QMenu,
                             QAction,
                             QTabWidget,
                             QCheckBox,
                             QInputDialog, 
                             QToolBar,
                             QTextBrowser)
from PyQt5.QtGui import (QFont,
                         QIcon)
import markdown
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bids_freesurfer import bids_freesurfer, bids_freesurfer_docker, find_subjects_and_sessions
import time



def launch(parent, add_info=None):
    """
    

    Parameters
    ----------
    parent : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    window = MainWindow(parent, add_info)
    window.show()



# =============================================================================
# MainWindow
# =============================================================================
class MainWindow(QMainWindow):
    """
    """
    

    def __init__(self, parent, add_info):
        """
        

        Parameters
        ----------
        parent : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        super().__init__()
        self.parent = parent
        self.bids = self.parent.bids
        self.add_info = add_info

        self.setWindowTitle("FreeSurfer recon-all")
        self.window = QWidget(self)
        self.setCentralWidget(self.window)
        self.center()
        
        # Create a toolbar and add it to the main window
        self.toolbar = QToolBar("Help?")
        self.addToolBar(self.toolbar)
        
        # Create an action
        help_action = QAction("Help?", self)
        help_action.triggered.connect(self.show_help)  # Connect to function

        # Add action to the toolbar
        self.toolbar.addAction(help_action)
        
        self.pipeline = "FreeSurfer"
        
        sss_slurm = self.add_info.get('sss_slurm')
        
        if sss_slurm == None:
        
            self.tab = FreeSurferTab(self, sss_slurm)
            layout = QVBoxLayout()
            layout.addWidget(self.tab)
            
        else:
            # get job_info
            path = os.path.dirname(os.path.abspath(__file__))
            
            if not pexists(pjoin(path, sss_slurm)):
                print('[ERROR] sss_slurm json file not found')
            
            self.job_json = None
            with open(pjoin(path, sss_slurm), 'r') as f:
                self.job_json = json.load(f)
            
            self.tabs = QTabWidget(self)
            
            self.main_tab = FreeSurferTab(self, sss_slurm)
            self.job_tab = JobTab(self, self.job_json["slurm_infos"])
            
            self.tabs.addTab(self.main_tab, "Main")
            self.tabs.addTab(self.job_tab, "Slurm Job")
            
            layout = QVBoxLayout()
            layout.addWidget(self.tabs)

        self.window.setLayout(layout)


    def center(self):
        """
        

        Returns
        -------
        None.

        """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        

    def event(self, event):
        # Override the help button event
        if event.type() == QEvent.NonClientAreaMouseButtonPress:
            if self.windowFlags() & Qt.WindowContextHelpButtonHint:
                self.show_help()
                return True
        return super().event(event)

    def show_help(self):
        # Open the help window with the Markdown file
        markdown_path = pjoin(os.path.dirname(__file__), "..", "README.md")
        if pexists(markdown_path):
            self.help_window = HelpWindow(markdown_path)
            self.help_window.show()
        else:
            print('Readme not found')
            
            
class HelpWindow(QWidget):
    def __init__(self, markdown_file):
        super().__init__()
        self.setWindowTitle("Help")
        self.resize(600, 400)

        # Load and convert markdown to HTML
        with open(markdown_file, 'r') as file:
            markdown_content = file.read()
        html_content = markdown.markdown(markdown_content)

        # Setup QTextBrowser to display the HTML content
        self.text_browser = QTextBrowser()
        self.text_browser.setHtml(html_content)

        layout = QVBoxLayout()
        layout.addWidget(self.text_browser)
        self.setLayout(layout)



# =============================================================================
# TemplateTab
# =============================================================================
class FreeSurferTab(QWidget):
    """
    """
    

    def __init__(self, parent, sss_slurm=None):
        """
        

        Parameters
        ----------
        parent : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        super().__init__()
        self.parent = parent
        self.bids = self.parent.bids
        self.bmat_path = self.parent.parent.bmat_path
        self.setMinimumSize(500, 200)
        
        self.pipeline = self.parent.pipeline
        
        self.local = sss_slurm == None
        
        if not self.local:
            self.job_json = self.parent.job_json
        
        # self.label = QLabel("This is a Template Pipeline")
        self.mprage_input = QLineEdit(self)
        self.mprage_input.setPlaceholderText("Select MPRAGE image (in anat folder)")
        
        self.subjects_input = QLineEdit(self)
        self.subjects_input.setPlaceholderText("Select subjects")

        self.sessions_input = QLineEdit(self)
        self.sessions_input.setPlaceholderText("Select sessions")
        
        self.overwrite = QCheckBox('Overwrite previous run')
        
        self.add_t2_check = QCheckBox('Add supplementary T2')
        self.t2_input = QLineEdit(self)
        self.t2_input.setPlaceholderText("Select T2 image")
        
        self.add_flair_check = QCheckBox('Add supplementary FLAIR')
        self.flair_input = QLineEdit(self)
        self.flair_input.setPlaceholderText("Select FLAIR image")
        
        self.button = QPushButton("Recon-all")
        self.button.clicked.connect(self.action)
        
        layout = QVBoxLayout()
        layout.addWidget(self.mprage_input)
        layout.addWidget(self.subjects_input)
        layout.addWidget(self.sessions_input)
        layout.addWidget(self.overwrite)
        t2_layout = QHBoxLayout()
        t2_layout.addWidget(self.add_t2_check)
        t2_layout.addWidget(self.t2_input)
        layout.addLayout(t2_layout)
        flair_layout = QHBoxLayout()
        flair_layout.addWidget(self.add_flair_check)
        flair_layout.addWidget(self.flair_input)
        layout.addLayout(flair_layout)
        layout.addWidget(self.button)
        
        self.setLayout(layout)


    def action(self):
        """
        

        Returns
        -------
        None.

        """
        
        # select sub and ses to run
        sub = self.subjects_input.text()
        ses = self.sessions_input.text()
        
        # select others arguments
        mprage = self.mprage_input.text()
        if self.add_t2_check.isChecked():
            t2 = self.t2_input.text()
        else:
            t2 = None
            
        if self.add_flair_check.isChecked():
            flair = self.flair_input.text()
        else:
            flair = None
            
        overwrite = self.overwrite.isChecked()
        
        if self.local:
            use_docker = self.parent.add_info.get('use_docker')
            self.thread = QThread()
            self.action = ActionWorker(self.bids.root_dir, sub, ses, self.pipeline, mprage, t2, flair, overwrite, use_docker=use_docker)
            self.action.moveToThread(self.thread)
            self.thread.started.connect(self.action.run)
            self.action.in_progress.connect(self.is_in_progress)
            self.action.finished.connect(self.thread.quit)
            self.action.finished.connect(self.action.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.start()
        
            self.parent.hide()
            
        else:
            self.job_json["slurm_infos"] = self.parent.job_tab.get_slurm_job_info()
            if self.job_json["slurm_infos"]["use_local"]:
                self.local = True
                self.action()
                return
            
            else:
                self.job_json["slurm_infos"].pop("use_local")
                
            # Import the submit_job_sss
            sys.path.insert(0, self.bmat_path)
            submit_job_sss = __import__('submit_job_sss')
            submit_job = submit_job_sss.submit_job
            sys.path.pop(0)
            
            # Do action
            def getPassword():
                password, ok = QInputDialog.getText(self, "SSH Key Passphrase", "Unlocking SSH key with passphrase?", 
                                        QLineEdit.Password)
                passphrase = None
                if ok and password:
                    passphrase = password
                return passphrase
            
            passphrase = getPassword()
                        
            cpus = self.job_json["slurm_infos"].get("cpus-per-task")
            # setup args
            args = []
            args.extend(['--mprage', mprage])
            if t2:
                args.extend(['--t2', t2])
            if flair:
                args.extend(['--flair', flair])
            if overwrite:
                args.append('--overwrite')
            if cpus:
                args.extend(['--cpus', cpus])
            
            # Do the job here and not in a thread 
            self.is_in_progress(('FreeSurfer', True))
            jobs_submitted = []
                
            try:
                job_id = submit_job(self.bids.root_dir, sub, ses, self.job_json, args=args, use_asyncssh=True, passphrase=passphrase, one_job=False)
                # job_id = ['Submitted batch job 2447621']
                if job_id is not None and job_id != []:
                    if type(job_id) is list:
                        jobs_submitted.extend(job_id)
                    else:
                        jobs_submitted.append(job_id)

            except Exception as e:
                self.error_handler(e)
            
            self.is_in_progress(('FreeSurfer', False))
            self.submitted_jobs(jobs_submitted)
            
    def is_in_progress(self, in_progress):
        self.parent.parent.work_in_progress.update_work_in_progress(in_progress)
        
    
    def error_handler(self, exception):
        QMessageBox.critical(self, type(exception).__name__, str(exception))
        
    def submitted_jobs(self, jobs_id):
        print('submitted jobs')
        class SubmittedJobsDialog(QDialog):
            def __init__(self, results, parent=None):
                super().__init__()
        
                self.setWindowTitle('Jobs Submitted')
                self.setGeometry(300, 300, 400, 300)
                
                layout = QVBoxLayout(self)
                
                # Create and populate the QListWidget
                self.listWidget = QListWidget(self)
                for result in results:
                    self.listWidget.addItem(result)
                
                layout.addWidget(self.listWidget)
        
                # Create OK button
                self.okButton = QPushButton('OK', self)
                self.okButton.clicked.connect(self.accept)
                
                # Add OK button to layout
                buttonLayout = QHBoxLayout()
                buttonLayout.addStretch()
                buttonLayout.addWidget(self.okButton)
                
                layout.addLayout(buttonLayout)
                
        job_dialog = SubmittedJobsDialog(jobs_id)
        # job_submitted_window = QMainWindow()
        # job_submitted_window.setCentralWidget(job_dialog)
        job_dialog.exec_()
        
        

class JobTab(QWidget):
    """
    """
    
    def __init__(self, parent, slurm_infos):
        """
        

        Returns
        -------
        None.

        """
        super().__init__()
        
        self.parent = parent
        self.bids = self.parent.bids
        self.slurm_info = slurm_infos
        self.setMinimumSize(500, 200)
        
        self.use_local_check = QCheckBox('Use local instead of server pipeline')
        
        self.slurm_info_input = {}
        layout = QVBoxLayout()
        layout.addWidget(self.use_local_check)
        for key in self.slurm_info.keys():
            key_label = QLabel(key)
            key_input = QLineEdit(self)
            key_input.setPlaceholderText(self.slurm_info[key])
            key_layout = QHBoxLayout()
            self.slurm_info_input[f'{key}_input'] = key_input
            key_layout.addWidget(key_label)
            key_layout.addWidget(key_input)
            layout.addLayout(key_layout)
            
        self.setLayout(layout)
            
            
    def get_slurm_job_info(self):
        use_local = self.use_local_check.isChecked()
        slurm_job_info = {"use_local":use_local}
        for key in self.slurm_info.keys():
            key_text = self.slurm_info_input[f'{key}_input'].text()
            if key_text == None or key_text == "":
                key_text = self.slurm_info_input[f'{key}_input'].placeholderText()
                
            slurm_job_info[key] = key_text
        return slurm_job_info



# =============================================================================
# ActionWorker
# =============================================================================
class ActionWorker(QObject):
    """
    """
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    in_progress = pyqtSignal(tuple)
    

    def __init__(self, bids, sub, ses, pipeline, mprage, t2, flair, overwrite, use_docker=False):
        """
        

        Returns
        -------
        None.

        """
        super().__init__()
        
        self.bids = bids
        self.sub = sub
        self.ses = ses
        self.pipeline = pipeline
        self.mprage = mprage
        self.t2 = t2
        self.flair = flair
        self.overwrite = overwrite
        self.use_docker = use_docker
        

    def run(self):
        """
        

        Returns
        -------
        None.

        """
        self.in_progress.emit((self.pipeline, True))
        # Action
        subjects_and_sessions = find_subjects_and_sessions(self.bids, self.sub, self.ses)
        
        for sub, sess in subjects_and_sessions:
            for ses in sess:
                print(sub, ses)
                if self.use_docker:
                    print('use_docker')
                    bids_freesurfer_docker(self.bids, sub, ses, mprage=self.mprage, t2=self.t2, flair=self.flair, overwrite=self.overwrite)
                else:
                    bids_freesurfer(self.bids, sub, ses, mprage=self.mprage, t2=self.t2, flair=self.flair, overwrite=self.overwrite)

        self.in_progress.emit((self.pipeline, False))
        self.finished.emit()


