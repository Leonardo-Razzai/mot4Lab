import PySpin
from astropy.io import fits
import sys
import time
def init_camera() -> tuple:
    """
    Initialize the FLIR camera system and retrieve the first available camera.

    Returns
    -------
    tuple
        A tuple containing:
        - cam (PySpin.CameraPtr): The initialized camera object.
        - cam_list (PySpin.CameraList): List of connected cameras.
        - system (PySpin.SystemPtr): PySpin system instance.
    """
    cam = None

    try:
        system = PySpin.System.GetInstance()
        cam_list = system.GetCameras()
        cam = cam_list.GetByIndex(0)
        cam.Init()
        
        print('*** CAMERA INITIALIZED *** \n')

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
    
    return cam, cam_list, system
  

class Cam:
  
    def __init__(self):
        self.cam, self.camlist, self.system = init_camera()
        
        self.Init()
        self.Set_Exposure()

    def Init(self):
        """
        Configure the camera to use a hardware or software trigger.

        Ensures the trigger mode is off before setting the trigger source and activation type. 
        Finally, enables the trigger mode for the camera to capture a single image upon trigger.

        """

        try:

            if self.cam.TriggerMode.GetAccessMode() != PySpin.RW:
                print('Unable to disable trigger mode (node retrieval). Aborting...')
                return False
            
            self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
            print('Trigger mode disabled...')
            time.sleep(1)
            self.cam.TriggerSource.SetValue(PySpin.TriggerSelector_FrameStart)
            print('Trigger selector set to frame start...')

            self.cam.TriggerSource.SetValue(PySpin.TriggerSource_Line0)
            print('Trigger source set to Line 0...')

            self.cam.TriggerActivation.SetValue(PySpin.TriggerActivation_RisingEdge)
            print('Trigger activation set to RisingEdge...')
            
            self.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
            print('Trigger mode turned back on...\n')
            
            print('*** TRIGGER CONFIGURED ***\n')
            
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            
    
    def Set_Exposure(self, exposure_time=1000):
        """
        Set the exposure time on the camera.

        Parameters
        ----------
        exposure_time : int, optional
            The exposure time to set in microseconds. Default is 1000.
        """
        try:
            self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
            print('Exposure auto set to off...')

            self.cam.ExposureTime.SetValue(exposure_time)
            print(f'Exposure time set to {exposure_time} us...\n')
            
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
        
    def Set_Gain(self, gain=17.8): # gain in dB
        """
        Set the gain on the camera.

        Parameters
        ----------
        exposure_time : float, optional
            The gain to set in microseconds. Default is 1000.
        """
        try:
            self.cam.GainAuto.SetValue(PySpin.GainAuto_Off)
            print('Gain auto set to off...')

            self.cam.Gain.SetValue(gain)
            print(f'Gain set to {gain} dB...\n')
            
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)


    def Start_Acquisition(self, mode='continuous'):
        """
        Start image acquisition on the camera in continuous mode.

        Sets the camera acquisition mode to continuous and begins acquisition. 
        This function assumes an external trigger will control the capture timing.
        """
        
        print('*** IMAGE ACQUISITION ***\n')
        
        try:
            if self.cam.AcquisitionMode.GetAccessMode() != PySpin.RW:
                print('Unable to set acquisition mode. Aborting...')
                return False
            
            if mode == 'continuous':
                self.cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
                print('Acquisition mode set to continuous...')
            elif mode == 'single':
                self.cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_SingleFrame)
                print('Acquisition mode set to single frame...')

            self.cam.BeginAcquisition()
            print('Acquiring images: waiting for external trigger')
            
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)

    def Get_Image(self):
        """
        Retrieve the next image from the camera.

        Blocks until an image is received or the timeout expires.

        Returns
        -------
        PySpin.ImagePtr or None
            The retrieved image object, or None if an error occurs.
        """
        image_result = None
        try:
            image_result = self.cam.GetNextImage(500)
            print('*** GOT AN IMAGE ***\n')
            
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            
        return image_result

    def Save_Image(self, image_result, filename='Triggered_image'):
        """
        Save a captured image to a file after converting its format.

        The image is converted to mono8 format and saved with the specified filename. 
        Basic image information such as width and height is also printed.

        Parameters
        ----------
        image_result : PySpin.ImagePtr
            The captured image to process and save.
        filename : str, optional
            The filename to save the image as. Default is 'Triggered_image'.
        """
        try:
            # Save as fits file
            image_data = image_result.GetNDArray()
            hdu = fits.PrimaryHDU(image_data)
            hdu.writeto(filename+'.fits', overwrite=True)
            print(f'FITS file saved at {filename}.fits\n')
            
            # Save as jpg file
            processor = PySpin.ImageProcessor()
            processor.SetColorProcessing(PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR)

            image_converted = processor.Convert(image_result, PySpin.PixelFormat_Mono8)
            image_converted.Save(filename+'.jpg')
            print(f'Image saved at {filename}.jpg\n')

            image_result.Release()
            
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)

    def Reset_Trigger(self):
        """
        Reset the camera by disabling the trigger mode.

        """
        try:
            result = True

            if self.cam.TriggerMode.GetAccessMode() != PySpin.RW:
                print('Unable to disable trigger mode (node retrieval). Aborting...')
                return False
            
            self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
            print('Trigger mode disabled...')
            
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

        return result

    def Close(self):
        """
        End image acquisition, deinitialize the camera, and release system resources.

        Cleans up by stopping acquisition, deinitializing the camera, clearing the camera list, 
        and releasing the PySpin system instance.
        """
        try:
            self.Reset_Trigger()
            self.cam.EndAcquisition()
            self.cam.DeInit()
            time.sleep(1)
            self.camlist.Clear()
            time.sleep(1)
            self.system.ReleaseInstance()
            print('Camera correctly closed.')
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
