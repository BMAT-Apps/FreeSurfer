#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 14:04:17 2024

@author: colin
"""

import os
from os.path import join as pjoin
from os.path import exists as pexists
import sys
import argparse
import shutil
# import time
import subprocess


def bids_freesurfer(bids, sub, ses, mprage='acq-MPRAGE_T1w', t2=None, flair=None, overwrite=False, cpus=None):
    
    # recon-all -i " + os.path.join(folder_path,subj) + " -subjid " +subj[:8] + " -all -openmp " + str(core_count) + " ",
    sub_ses_anat = pjoin(bids, f'sub-{sub}', f'ses-{ses}', 'anat')
    sub_ses_fs = pjoin(bids, 'derivatives', 'FreeSurfer', f'sub-{sub}', f'ses-{ses}')
    
    if not pexists(pjoin(sub_ses_anat, f'sub-{sub}_ses-{ses}_{mprage}.nii.gz')):
        print(f'[ERROR] MPRAGE image does not exists')
        raise FileNotFoundError(f"[ERROR] {pjoin(sub_ses_anat, f'sub-{sub}_ses-{ses}_{mprage}.nii.gz')} MPRAGE image does not exists")
    
    if t2:
        if not pexists(pjoin(sub_ses_anat, f'sub-{sub}_ses-{ses}_{t2}.nii.gz')):
            print('[ERROR] T2w image does not exists')
            raise FileNotFoundError('[ERROR] T2w image does not exists')
        
    if flair:
        if not pexists(pjoin(sub_ses_anat, f'sub-{sub}_ses-{ses}_{flair}.nii.gz')):
            print('[ERROR] FLAIR image does not exists')
            raise FileNotFoundError('[ERROR] FLAIR image does not exists')
    
    # if not pexists(sub_ses_fs):
    #     os.makedirs(sub_ses_fs)
    if pexists(sub_ses_fs):
        print('[WARNING] subject session FreeSurfer folder already exists! Use overwrite to re-run FreeSurfer')
        if overwrite:
            print('overwrite...')
            shutil.rmtree(sub_ses_fs)
        
    fs_subdir = pjoin(bids, 'derivatives', 'FreeSurfer', f'sub-{sub}')
    if not pexists(fs_subdir):
        os.makedirs(fs_subdir, exist_ok=True)
    fs_subid = f'ses-{ses}'
    
    if cpus:
        fs_cpu = f'-openmp {cpus}'
    else:
        fs_cpu = ''
        
    # subprocess.Popen(f"alias /bin/tcsh=$(which tcsh)", shell=True).wait()
                    
    if t2 and flair:
        subprocess.Popen(f"recon-all -i {pjoin(sub_ses_anat, f'sub-{sub}_ses-{ses}_{mprage}.nii.gz')} -sd {fs_subdir} -subjid {fs_subid} -FLAIR {pjoin(sub_ses_anat, f'sub-{sub}_ses-{ses}_{flair}.nii.gz')} -all {fs_cpu}", shell=True).wait()
    elif t2:
        subprocess.Popen(f"recon-all -i {pjoin(sub_ses_anat, f'sub-{sub}_ses-{ses}_{mprage}.nii.gz')} -sd {fs_subdir} -subjid {fs_subid} -T2 {pjoin(sub_ses_anat, f'sub-{sub}_ses-{ses}_{t2}.nii.gz')} -all {fs_cpu}", shell=True).wait()
    elif flair:
        subprocess.Popen(f"recon-all -i {pjoin(sub_ses_anat, f'sub-{sub}_ses-{ses}_{mprage}.nii.gz')} -sd {fs_subdir} -subjid {fs_subid} -FLAIR {pjoin(sub_ses_anat, f'sub-{sub}_ses-{ses}_{flair}.nii.gz')} -all {fs_cpu}", shell=True).wait()
    else:
        subprocess.Popen(f"recon-all -i {pjoin(sub_ses_anat, f'sub-{sub}_ses-{ses}_{mprage}.nii.gz')} -sd {fs_subdir} -subjid {fs_subid} -all {fs_cpu}", shell=True).wait()


def bids_freesurfer_docker(bids, sub, ses, mprage='acq-MPRAGE_T1w', t2=None, flair=None, overwrite=False, cpus=None):
    
    path = os.path.dirname(os.path.abspath(__file__))
    fs_license = pjoin(path, 'license.txt')
    
    # recon-all -i " + os.path.join(folder_path,subj) + " -subjid " +subj[:8] + " -all -openmp " + str(core_count) + " ",
    sub_ses_anat = pjoin(bids, f'sub-{sub}', f'ses-{ses}', 'anat')
    sub_ses_fs = pjoin(bids, 'derivatives', 'FreeSurfer', f'sub-{sub}', f'ses-{ses}')
    
    if not pexists(pjoin(sub_ses_anat, f'sub-{sub}_ses-{ses}_{mprage}.nii.gz')):
        print(f'[ERROR] MPRAGE image does not exists')
        raise FileNotFoundError(f"[ERROR] {pjoin(sub_ses_anat, f'sub-{sub}_ses-{ses}_{mprage}.nii.gz')} MPRAGE image does not exists")
    
    if t2:
        if not pexists(pjoin(sub_ses_anat, f'sub-{sub}_ses-{ses}_{t2}.nii.gz')):
            print('[ERROR] T2w image does not exists')
            raise FileNotFoundError('[ERROR] T2w image does not exists')
        
    if flair:
        if not pexists(pjoin(sub_ses_anat, f'sub-{sub}_ses-{ses}_{flair}.nii.gz')):
            print('[ERROR] FLAIR image does not exists')
            raise FileNotFoundError('[ERROR] FLAIR image does not exists')
    
    # if not pexists(sub_ses_fs):
    #     os.makedirs(sub_ses_fs)
    if pexists(sub_ses_fs):
        print('[WARNING] subject session FreeSurfer folder already exists! Use overwrite to re-run FreeSurfer')
        if overwrite:
            print('overwrite...')
            shutil.rmtree(sub_ses_fs)
        
    fs_subdir = pjoin(bids, 'derivatives', 'FreeSurfer', f'sub-{sub}')
    if not pexists(fs_subdir):
        os.makedirs(fs_subdir, exist_ok=True)
    fs_subid = f'ses-{ses}'
    
    if cpus:
        fs_cpu = f'-openmp {cpus}'
    else:
        fs_cpu = ''
        
    # subprocess.Popen(f"alias /bin/tcsh=$(which tcsh)", shell=True).wait()
                    
    if t2 and flair:
        subprocess.Popen(f"docker run --rm --privileged -v {fs_license}:/usr/local/freesurfer/license.txt -v {sub_ses_anat}:/media/anat -v {fs_subdir}:/media/freesurfer_subjects freesurfer:7.3.2 recon-all -i {pjoin('/media/anat', f'sub-{sub}_ses-{ses}_{mprage}.nii.gz')} -sd /media/freesurfer_subjects -subjid {fs_subid} -FLAIR {pjoin('/media/anat', f'sub-{sub}_ses-{ses}_{flair}.nii.gz')} -all {fs_cpu}", shell=True).wait()
    elif t2:
        subprocess.Popen(f"docker run --rm --privileged -v {fs_license}:/usr/local/freesurfer/license.txt -v {sub_ses_anat}:/media/anat -v {fs_subdir}:/media/freesurfer_subjects freesurfer:7.3.2 recon-all -i {pjoin('/media/anat', f'sub-{sub}_ses-{ses}_{mprage}.nii.gz')} -sd /media/freesurfer_subjects -subjid {fs_subid} -T2 {pjoin('/media/anat', f'sub-{sub}_ses-{ses}_{t2}.nii.gz')} -all {fs_cpu}", shell=True).wait()
    elif flair:
        subprocess.Popen(f"docker run --rm --privileged -v {fs_license}:/usr/local/freesurfer/license.txt -v {sub_ses_anat}:/media/anat -v {fs_subdir}:/media/freesurfer_subjects freesurfer:7.3.2 recon-all -i {pjoin('/media/anat', f'sub-{sub}_ses-{ses}_{mprage}.nii.gz')} -sd /media/freesurfer_subjects -subjid {fs_subid} -FLAIR {pjoin('/media/anat', f'sub-{sub}_ses-{ses}_{flair}.nii.gz')} -all {fs_cpu}", shell=True).wait()
    else:
        subprocess.Popen(f"docker run --rm --privileged -v {fs_license}:/usr/local/freesurfer/license.txt -v {sub_ses_anat}:/media/anat -v {fs_subdir}:/media/freesurfer_subjects freesurfer:7.3.2 recon-all -i {pjoin('/media/anat', f'sub-{sub}_ses-{ses}_{mprage}.nii.gz')} -sd /media/freesurfer_subjects -subjid {fs_subid} -all {fs_cpu}", shell=True).wait()



def get_session_list(bids, subj, ses_details):
    """Helper function to get the list of sessions for a given subject."""
    sess = []
    if ses_details == 'all':
        for d in os.listdir(pjoin(bids, f'sub-{subj}')):
            if d.startswith('ses-'):
                sess.append(d.split('-')[1])
    else:
        for s in ses_details.split(','):
            if '-' in s:
                s0, s1 = map(int, s.split('-'))
                for si in range(s0, s1 + 1):
                    si_str = str(si).zfill(2)
                    if os.path.isdir(pjoin(bids, f'sub-{subj}', f'ses-{si_str}')):
                        sess.append(si_str)
            else:
                if os.path.isdir(pjoin(bids, f'sub-{subj}', f'ses-{s}')):
                    sess.append(s)
    return sess

def process_subject_range(bids, sub_range, ses_details):
    """Helper function to process a range of subjects."""
    subjects_and_sessions = []
    sub0, sub1 = map(int, sub_range.split('-'))
    for subi in range(sub0, sub1 + 1):
        subi_str = str(subi).zfill(3)
        if not os.path.isdir(pjoin(bids, f'sub-{subi_str}')):
            continue
        sess = get_session_list(bids, subi_str, ses_details)
        subjects_and_sessions.append((subi_str, sess))
    return subjects_and_sessions

def find_subjects_and_sessions(bids, sub, ses):
    subjects_and_sessions = []

    if sub == 'all':
        # Process all subjects
        for dirs in os.listdir(bids):
            if dirs.startswith('sub-'):
                subj = dirs.split('-')[1]
                sess = get_session_list(bids, subj, ses)
                subjects_and_sessions.append((subj, sess))
    else:
        # Process specified subjects
        for sub_item in sub.split(','):
            if '-' in sub_item:
                subjects_and_sessions.extend(process_subject_range(bids, sub_item, ses))
            else:
                if not os.path.isdir(pjoin(bids, f'sub-{sub_item}')):
                    continue
                sess = get_session_list(bids, sub_item, ses)
                subjects_and_sessions.append((sub_item, sess))
    
    return sorted(subjects_and_sessions)
    


if __name__ == '__main__':
    
    description = '''
bids_freesurfer:
    Script to run FreeSurfer recon-all
    '''
    
    usage = '\npython %(prog)s bids sub ses [OPTIONS]'
    
    parser = argparse.ArgumentParser(description=description, usage=usage)
    
    parser.add_argument('bids', type=str, help='path towards a bids formatted database')
    parser.add_argument('sub', type=str, help='sub ID or list of sub ID to process (e.g. 001,002). The keyword "all" will select all subjects of the database, while "-" allow to select subject ID in between two border (e.g. 001-010)')
    parser.add_argument('ses', type=str, help='ses ID or list of ses ID to process (e.g. 01,02). The keyword "all" will select all sessions of the database, while "-" allow to select session ID in between two border (e.g. 01-10)')
    parser.add_argument('--mprage', dest='mprage', type=str, help='name of the mprage image', default='acq-MPRAGE_T1w')
    parser.add_argument('--t2', dest='t2', type=str, help='name of a supplementary T2w image for recon-all', required=False)
    parser.add_argument('--flair', dest='flair', type=str, help='name of a supplementary FLAIR image for recon-all', required=False)
    parser.add_argument('--overwrite', dest='overwrite', help='Overwrite existing data if subject has already been runned (default: False)', action='store_const', const=True, default=False, required=False)
    parser.add_argument('--cpus', dest='cpus', type=str, help='number of cpus on which to run recon-all', required=False)
    parser.add_argument('--use-docker', dest='use_docker', help='use docker version of FreeSurfer instead of local one (default=False)', action='store_const', const=True, default=False, required=False)
    
    # Parse the arguments
    try:
        args = parser.parse_args()
    except SystemExit as e:
        # This block catches the SystemExit exception raised by argparse when required args are missing
        if e.code != 0:  # Non-zero code indicates an error
            parser.print_help()
        sys.exit(e.code)
        
    bids = args.bids
    mprage = args.mprage
    t2 = args.t2
    flair = args.flair
    cpus = args.cpus
    
    subjects_and_sessions = find_subjects_and_sessions(bids, args.sub, args.ses)
    
    for sub, sess in subjects_and_sessions:
        for ses in sess:
            print(sub, ses)
            
            if args.use_docker:
                bids_freesurfer_docker(bids, sub, ses, mprage=mprage, t2=t2, flair=flair, cpus=cpus)
            else:
                bids_freesurfer(bids, sub, ses, mprage=mprage, t2=t2, flair=flair, cpus=cpus)
    
    