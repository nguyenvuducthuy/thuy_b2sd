Add-Type -AssemblyName System.Windows.Forms

$Form = New-Object System.Windows.Forms.Form
$Form.width = 400
$Form.height = 430
$Form.Text = 'SDEnvBuilder - anhungxadieu'

$rootLabel = New-Object System.Windows.Forms.Label
$rootLabel.Location = '10,10'
$rootLabel.Size = '40,20'
$rootLabel.Text = 'root:'
$Form.Controls.Add($rootLabel)

$rootDir = New-Object System.Windows.Forms.TextBox
$rootDir.Text = $env:TEMP+"\thuy"
$rootDir.Location = '50,10'
$rootDir.Size = '320,100'
$Form.Controls.Add($rootDir)

$checkedlistbox=New-Object System.Windows.Forms.CheckedListBox
$checkedlistbox.Location = '10,40'
$checkedlistbox.Size = '360,300'

$form.Controls.Add($checkedlistbox)

if ($null -ne $CheckedListBox)
{
    $CheckedListBox.Items.Add("install_scoop") | Out-Null;
    $CheckedListBox.Items.Add("install_miniconda3") | Out-Null;
    $CheckedListBox.Items.Add("get_stable_diffusion") | Out-Null;
    $CheckedListBox.Items.Add("get_b2sd") | Out-Null;    
    $CheckedListBox.Items.Add("get_control_net") | Out-Null;
    $CheckedListBox.Items.Add("run_stable_diffusion") | Out-Null;
}

$ApplyButton = new-object System.Windows.Forms.Button
$ApplyButton.Location = '10, 340'
$ApplyButton.Size = '360, 40'
$ApplyButton.Text = 'OK'
$ApplyButton.DialogResult = 'Ok'
$form.Controls.Add($ApplyButton)

$result = $Form.ShowDialog()

if ($result -eq [System.Windows.Forms.DialogResult]::OK)
{
    New-Item -ItemType Directory -Force -Path $rootDir.Text | Out-Null
    $sd_ext = $rootDir.Text+"\stable-diffusion-webui\extensions"
    $sd_root = $rootDir.Text+"\stable-diffusion-webui"
    $cn_model_root = $rootDir.Text+"\stable-diffusion-webui\extensions\sd-webui-controlnet\models"
    $x = $CheckedListBox.CheckedItems
    For ($i=0; $i -lt $x.count; $i++)
    {
        if($x[$i].toString() -eq "install_scoop")
        {
            Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
            irm get.scoop.sh | iex
            scoop bucket add extras
            scoop install git
            scoop install cmake
        }
        if($x[$i].toString() -eq "install_miniconda3")
        {
            scoop install miniconda3
        }
        if($x[$i].toString() -eq "get_stable_diffusion")
        {
            Set-Location $rootDir.Text
            git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
            cd stable-diffusion-webui
            conda env create -f environment-wsl2.yaml
            conda activate automatic
        }
        if($x[$i].toString() -eq "get_b2sd")
        {
            Set-Location $rootDir.Text
            git clone https://github.com/nguyenvuducthuy/thuy_b2sd.git
        }
        if($x[$i].toString() -eq "get_control_net")
        {
            Set-Location $sd_ext
            git clone https://github.com/Mikubill/sd-webui-controlnet.git
            git clone https://github.com/hnmr293/sd-webui-cutoff.git
            Set-Location $cn_model_root
            Invoke-WebRequest -Uri https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_canny-fp16.safetensors -OutFile control_canny-fp16.safetensors
            Invoke-WebRequest -Uri https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_depth-fp16.safetensors -OutFile control_depth-fp16.safetensors
            Invoke-WebRequest -Uri https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_hed-fp16.safetensors -OutFile control_hed-fp16.safetensors
            Invoke-WebRequest -Uri https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_mlsd-fp16.safetensors -OutFile control_mlsd-fp16.safetensors
            Invoke-WebRequest -Uri https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_normal-fp16.safetensors -OutFile control_normal-fp16.safetensors
            Invoke-WebRequest -Uri https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_openpose-fp16.safetensors -OutFile control_openpose-fp16.safetensors
            Invoke-WebRequest -Uri https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_scibble-fp16.safetensors -OutFile control_scibble-fp16.safetensors
            Invoke-WebRequest -Uri https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_seg-fp16.safetensors -OutFile control_seg-fp16.safetensors
        }
        if($x[$i].toString() -eq "run_stable_diffusion")
        {
            Set-Location $sd_root
            conda activate automatic
            python .\launch.py --api
        }
    }
}