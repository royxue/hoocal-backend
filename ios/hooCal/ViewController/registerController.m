//
//  registerController.m
//  hooCal
//
//  Created by zhongtoby on 14/11/15.
//  Copyright (c) 2014年 hang. All rights reserved.
//

#import "registerController.h"
#import "RegisterViewModel.h"
#import <SVProgressHUD.h>

@interface registerController ()<UITextFieldDelegate>
@property (strong, nonatomic) IBOutlet UITextField *nickName;
@property (strong, nonatomic) IBOutlet UITextField *email;
@property (strong, nonatomic) IBOutlet UITextField *psw;
@property (strong, nonatomic) IBOutlet UITextField *psw2;
@end

@implementation registerController
#pragma mark - action
- (IBAction)cancel:(id)sender {
    [self resignKeyboard];
    [self.navigationController dismissViewControllerAnimated:YES completion:nil];
}
- (IBAction)register:(id)sender {
    [self resignKeyboard];
    [SVProgressHUD showWithStatus:@"正在注册"];
    //    __weak UIViewController *weakSelf = self;
    [RegisterViewModel registerWithNickName:_nickName.text Email:_email.text Psw:_psw.text Psw2:_psw2.text Block:^(NSInteger state, NSDictionary *dict) {
        if (state == successful) {
            [SVProgressHUD dismiss];
            //            [self.navigationController dismissViewControllerAnimated:YES completion:^{
            //                [weakSelf performSegueWithIdentifier:@"sugueAfterSignIn" sender:weakSelf];
            //            }];
            [self performSegueWithIdentifier:@"segueAfterSignIn" sender:nil];
        } else {
            [SVProgressHUD showErrorWithStatus:@"注册失败"];
        }
    }];
}




- (void)touchesBegan:(NSSet *)touches withEvent:(UIEvent *)event {
    [self resignKeyboard];
}

#pragma mark - UITextFieldDelegate
- (BOOL)textFieldShouldReturn:(UITextField *)textField {
    NSInteger tag = textField.tag;
    if (tag == 1) {
        [_email becomeFirstResponder];
    } else if (tag == 2) {
        [_psw becomeFirstResponder];
    } else if (tag == 3) {
        [_psw2 becomeFirstResponder];
    } else {
        [textField resignFirstResponder];
        [self register:nil];
    }
    return YES;
}

#pragma mark - Tools
- (void)resignKeyboard {
    [_nickName resignFirstResponder];
    [_email resignFirstResponder];
    [_psw resignFirstResponder];
    [_psw2 resignFirstResponder];
}
@end
