import threading
import queue
import cv2

class VideoProcessor:
    def __init__(self, video_file):
        self.video_file = video_file
        self.frame_queue = queue.Queue(maxsize=10)
        self.gray_queue = queue.Queue(maxsize=10)
        self.frame_count = 0
        self.frame_completed = threading.Semaphore(0)
        self.gray_completed = threading.Semaphore(0)

    def extract_frames(self):
        cap = cv2.VideoCapture(self.video_file)
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                self.frame_queue.put(frame)
            else:
                break
        cap.release()
        self.frame_completed.release()

    def convert_to_gray(self):
        while True:
            frame = self.frame_queue.get()
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.gray_queue.put(gray_frame)
            self.frame_queue.task_done()
            if self.frame_queue.empty() and self.frame_completed._value == 1:
                self.gray_completed.release()
                break

    def display_frames(self):
        while True:
            gray_frame = self.gray_queue.get()
            cv2.imshow('Video', gray_frame)
            if cv2.waitKey(42) & 0xFF == ord('q'):
                break
            self.gray_queue.task_done()
            if self.gray_queue.empty() and self.gray_completed._value == 1:
                break

    def start(self):
        extract_thread = threading.Thread(target=self.extract_frames)
        convert_thread1 = threading.Thread(target=self.convert_to_gray)
        display_thread = threading.Thread(target=self.display_frames)

        extract_thread.start()
        convert_thread1.start()
        display_thread.start()

        extract_thread.join()
        self.frame_completed.acquire()
        self.frame_queue.join()
        self.gray_completed.acquire()
        self.gray_queue.join()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    video_processor = VideoProcessor('clip.mp4')
    video_processor.start()

