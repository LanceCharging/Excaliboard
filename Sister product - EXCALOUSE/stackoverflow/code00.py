import ctypes as ctypes
import ctypes.wintypes
import sys
import time

import ctypes_wrappers


HWND_MESSAGE = -3

WM_QUIT = 0x0012
WM_INPUT = 0x00FF
WM_KEYUP = 0x0101
WM_CHAR = 0x0102

HID_USAGE_PAGE_GENERIC = 0x01

RIDEV_NOLEGACY = 0x00000030
RIDEV_INPUTSINK = 0x00000100
RIDEV_CAPTUREMOUSE = 0x00000200

RID_HEADER = 0x10000005
RID_INPUT = 0x10000003

RIM_TYPEMOUSE = 0
RIM_TYPEKEYBOARD = 1
RIM_TYPEHID = 2

PM_NOREMOVE = 0x0000


def wnd_proc(hwnd, msg, wparam, lparam):
    print(
        f"Handle message - hwnd: 0x{hwnd:016X} msg: 0x{msg:08X} wp: 0x{wparam:016X} lp: 0x{lparam:016X}"
    )
    if msg == WM_INPUT:
        size = ctypes.wintypes.UINT(0)
        res = ctypes_wrappers.GetRawInputData(
            ctypes.cast(lparam, ctypes_wrappers.PRAWINPUT),
            RID_INPUT,
            None,
            ctypes.byref(size),
            ctypes.sizeof(ctypes_wrappers.RAWINPUTHEADER),
        )
        if res == ctypes.wintypes.UINT(-1) or size == 0:
            print_error(text="GetRawInputData 0")
            return 0
        buf = ctypes.create_string_buffer(size.value)
        res = ctypes_wrappers.GetRawInputData(
            ctypes.cast(lparam, ctypes_wrappers.PRAWINPUT),
            RID_INPUT,
            buf,
            ctypes.byref(size),
            ctypes.sizeof(ctypes_wrappers.RAWINPUTHEADER),
        )
        if res != size.value:
            print_error(text="GetRawInputData 1")
            return 0
        # print("kkt: ", ctypes.cast(lparam, ctypes_wrappers.PRAWINPUT).contents.to_string())
        ri = ctypes.cast(buf, ctypes_wrappers.PRAWINPUT).contents
        # print(ri.to_string())
        head = ri.header
        print(head.to_string())
        # print(ri.data.mouse.to_string())
        # print(ri.data.keyboard.to_string())
        # print(ri.data.hid.to_string())
        if head.dwType == RIM_TYPEMOUSE:
            data = ri.data.mouse
        elif head.dwType == RIM_TYPEKEYBOARD:
            data = ri.data.keyboard
            if data.VKey == 0x1B:
                ctypes_wrappers.PostQuitMessage(0)
        elif head.dwType == RIM_TYPEHID:
            data = ri.data.hid
        else:
            print("Wrong raw input type!!!")
            return 0
        print(data.to_string())
    return ctypes_wrappers.DefWindowProc(hwnd, msg, wparam, lparam)


def print_error(code=None, text=None):
    text = text + " - e" if text else "E"
    code = ctypes_wrappers.GetLastError() if code is None else code
    print(f"{text}rror code: {code}")


def register_devices(hwnd=None):
    flags = RIDEV_INPUTSINK  # @TODO - cfati: If setting to 0, GetMessage hangs
    generic_usage_ids = (0x01, 0x02, 0x04, 0x05, 0x06, 0x07, 0x08)
    devices = (ctypes_wrappers.RawInputDevice * len(generic_usage_ids))(
        *(
            ctypes_wrappers.RawInputDevice(HID_USAGE_PAGE_GENERIC, uid, flags, hwnd)
            for uid in generic_usage_ids
        )
    )
    # for d in devices: print(d.usUsagePage, d.usUsage, d.dwFlags, d.hwndTarget)
    if ctypes_wrappers.RegisterRawInputDevices(
        devices, len(generic_usage_ids), ctypes.sizeof(ctypes_wrappers.RawInputDevice)
    ):
        print("Successfully registered input device(s)!")
        return True
    else:
        print_error(text="RegisterRawInputDevices")
        return False


def main(*argv):
    wnd_cls = "SO049572093_RawInputWndClass"
    wcx = ctypes_wrappers.WNDCLASSEX()
    wcx.cbSize = ctypes.sizeof(ctypes_wrappers.WNDCLASSEX)
    # wcx.lpfnWndProc = ctypes.cast(ctypes_wrappers.DefWindowProc, ctypes.c_void_p)
    wcx.lpfnWndProc = ctypes_wrappers.WNDPROC(wnd_proc)
    wcx.hInstance = ctypes_wrappers.GetModuleHandle(None)
    wcx.lpszClassName = wnd_cls
    # print(dir(wcx))
    res = ctypes_wrappers.RegisterClassEx(ctypes.byref(wcx))
    if not res:
        print_error(text="RegisterClass")
        return 0
    hwnd = ctypes_wrappers.CreateWindowEx(
        0, wnd_cls, None, 0, 0, 0, 0, 0, 0, None, wcx.hInstance, None
    )
    if not hwnd:
        print_error(text="CreateWindowEx")
        return 0
    # print("hwnd:", hwnd)
    if not register_devices(hwnd):
        return 0
    msg = ctypes.wintypes.MSG()
    pmsg = ctypes.byref(msg)
    print("Start loop (press <ESC> to exit)...")
    while res := ctypes_wrappers.GetMessage(pmsg, None, 0, 0):
        if res < 0:
            print_error(text="GetMessage")
            break
        ctypes_wrappers.TranslateMessage(pmsg)
        ctypes_wrappers.DispatchMessage(pmsg)


if __name__ == "__main__":
    print(
        "Python {:s} {:03d}bit on {:s}\n".format(
            " ".join(elem.strip() for elem in sys.version.split("\n")),
            64 if sys.maxsize > 0x100000000 else 32,
            sys.platform,
        )
    )
    rc = main(*sys.argv[1:])
    print("\nDone.\n")
    sys.exit(rc)
