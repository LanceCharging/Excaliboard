import ctypes
import ctypes.wintypes


HCURSOR = ctypes.c_void_p
LRESULT = ctypes.c_ssize_t

wndproc_args = (
    ctypes.wintypes.HWND,
    ctypes.wintypes.UINT,
    ctypes.wintypes.WPARAM,
    ctypes.wintypes.LPARAM,
)

WNDPROC = ctypes.CFUNCTYPE(LRESULT, *wndproc_args)

kernel32 = ctypes.WinDLL("Kernel32")
user32 = ctypes.WinDLL("User32")


def structure_to_string_method(self):
    ret = [
        f"{self.__class__.__name__} (size: {ctypes.sizeof(self.__class__)}) instance at 0x{id(self):016X}:"
    ]
    for fn, _ in self._fields_:
        ret.append(f"  {fn}: {getattr(self, fn)}")
    return "\n".join(ret) + "\n"


union_to_string_method = structure_to_string_method


class Struct(ctypes.Structure):
    to_string = structure_to_string_method


class Uni(ctypes.Union):
    to_string = union_to_string_method


class WNDCLASSEXW(Struct):
    _fields_ = (
        ("cbSize", ctypes.wintypes.UINT),
        ("style", ctypes.wintypes.UINT),
        # ("lpfnWndProc", ctypes.c_void_p),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", ctypes.wintypes.HINSTANCE),
        ("hIcon", ctypes.wintypes.HICON),
        ("hCursor", HCURSOR),
        ("hbrBackground", ctypes.wintypes.HBRUSH),
        ("lpszMenuName", ctypes.wintypes.LPCWSTR),
        ("lpszClassName", ctypes.wintypes.LPCWSTR),
        ("hIconSm", ctypes.wintypes.HICON),
    )


WNDCLASSEX = WNDCLASSEXW


class RawInputDevice(Struct):
    _fields_ = (
        ("usUsagePage", ctypes.wintypes.USHORT),
        ("usUsage", ctypes.wintypes.USHORT),
        ("dwFlags", ctypes.wintypes.DWORD),
        ("hwndTarget", ctypes.wintypes.HWND),
    )


PRawInputDevice = ctypes.POINTER(RawInputDevice)


class RAWINPUTHEADER(Struct):
    _fields_ = (
        ("dwType", ctypes.wintypes.DWORD),
        ("dwSize", ctypes.wintypes.DWORD),
        ("hDevice", ctypes.wintypes.HANDLE),
        ("wParam", ctypes.wintypes.WPARAM),
    )


class RAWMOUSE(Struct):
    _fields_ = (
        ("usFlags", ctypes.wintypes.USHORT),
        ("ulButtons", ctypes.wintypes.ULONG),  # unnamed union: 2 USHORTS: flags, data
        ("ulRawButtons", ctypes.wintypes.ULONG),
        ("lLastX", ctypes.wintypes.LONG),
        ("lLastY", ctypes.wintypes.LONG),
        ("ulExtraInformation", ctypes.wintypes.ULONG),
    )


class RAWKEYBOARD(Struct):
    _fields_ = (
        ("MakeCode", ctypes.wintypes.USHORT),
        ("Flags", ctypes.wintypes.USHORT),
        ("Reserved", ctypes.wintypes.USHORT),
        ("VKey", ctypes.wintypes.USHORT),
        ("Message", ctypes.wintypes.UINT),
        ("ExtraInformation", ctypes.wintypes.ULONG),
    )


class RAWHID(Struct):
    _fields_ = (
        ("dwSizeHid", ctypes.wintypes.DWORD),
        ("dwCount", ctypes.wintypes.DWORD),
        (
            "bRawData",
            ctypes.wintypes.BYTE * 1,
        ),  # @TODO - cfati: https://docs.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-rawhid, but not very usable via CTypes
    )


class RAWINPUT_U0(Uni):
    _fields_ = (
        ("mouse", RAWMOUSE),
        ("keyboard", RAWKEYBOARD),
        ("hid", RAWHID),
    )


class RAWINPUT(Struct):
    _fields_ = (
        ("header", RAWINPUTHEADER),
        ("data", RAWINPUT_U0),
    )


PRAWINPUT = ctypes.POINTER(RAWINPUT)


GetLastError = kernel32.GetLastError
GetLastError.argtypes = ()
GetLastError.restype = ctypes.wintypes.DWORD

GetModuleHandle = kernel32.GetModuleHandleW
GetModuleHandle.argtypes = (ctypes.wintypes.LPWSTR,)
GetModuleHandle.restype = ctypes.wintypes.HMODULE


DefWindowProc = user32.DefWindowProcW
DefWindowProc.argtypes = wndproc_args
DefWindowProc.restype = LRESULT

RegisterClassEx = user32.RegisterClassExW
RegisterClassEx.argtypes = (ctypes.POINTER(WNDCLASSEX),)
RegisterClassEx.restype = ctypes.wintypes.ATOM

CreateWindowEx = user32.CreateWindowExW
CreateWindowEx.argtypes = (
    ctypes.wintypes.DWORD,
    ctypes.wintypes.LPCWSTR,
    ctypes.wintypes.LPCWSTR,
    ctypes.wintypes.DWORD,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.wintypes.HWND,
    ctypes.wintypes.HMENU,
    ctypes.wintypes.HINSTANCE,
    ctypes.wintypes.LPVOID,
)
CreateWindowEx.restype = ctypes.wintypes.HWND

RegisterRawInputDevices = user32.RegisterRawInputDevices
RegisterRawInputDevices.argtypes = (
    PRawInputDevice,
    ctypes.wintypes.UINT,
    ctypes.wintypes.UINT,
)
RegisterRawInputDevices.restype = ctypes.wintypes.BOOL

GetRawInputData = user32.GetRawInputData
GetRawInputData.argtypes = (
    PRAWINPUT,
    ctypes.wintypes.UINT,
    ctypes.wintypes.LPVOID,
    ctypes.wintypes.PUINT,
    ctypes.wintypes.UINT,
)
GetRawInputData.restype = ctypes.wintypes.UINT

GetMessage = user32.GetMessageW
GetMessage.argtypes = (
    ctypes.wintypes.LPMSG,
    ctypes.wintypes.HWND,
    ctypes.wintypes.UINT,
    ctypes.wintypes.UINT,
)
GetMessage.restype = ctypes.wintypes.BOOL

PeekMessage = user32.PeekMessageW
PeekMessage.argtypes = (
    ctypes.wintypes.LPMSG,
    ctypes.wintypes.HWND,
    ctypes.wintypes.UINT,
    ctypes.wintypes.UINT,
    ctypes.wintypes.UINT,
)
PeekMessage.restype = ctypes.wintypes.BOOL

TranslateMessage = user32.TranslateMessage
TranslateMessage.argtypes = (ctypes.wintypes.LPMSG,)
TranslateMessage.restype = ctypes.wintypes.BOOL

DispatchMessage = user32.DispatchMessageW
DispatchMessage.argtypes = (ctypes.wintypes.LPMSG,)
DispatchMessage.restype = LRESULT

PostQuitMessage = user32.PostQuitMessage
PostQuitMessage.argtypes = (ctypes.c_int,)
PostQuitMessage.restype = None
